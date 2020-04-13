from stravalib.client import Client
import time
import os
import json


class StravaImporter:

    def __init__(self, s3_file_manager):
        self.s3_file_manager = s3_file_manager
        self.client = self.create_client()
        self.environment = os.getenv('ENVIRONMENT')
        self.workout_to_process_dir = self.environment + '/workout-to-process/'
        self.workout_archive_dir = self.environment + '/archive/'

    def main(self):
        workout_file_path = self.get_workout_to_process_file_path()
        if workout_file_path is None:
            return
        print('About to upload workout: ' + self.get_workout_id(workout_file_path))
        self.upload_workout(workout_file_path)
        print('Workout uploaded to Strava!')
        self.move_workout_to_archive(workout_file_path)

    def create_client(self):
        self.s3_file_manager.download_file('strava_auth.json', '/tmp/strava_auth.json')
        with open('/tmp/strava_auth.json') as auth_json:
            data = json.load(auth_json)
            access_token = data['access_token']
            refresh_token = data['refresh_token']
            expires_at = data['expires_at']

        client = Client()
        client.access_token = access_token
        client.refresh_token = refresh_token
        client.token_expires_at = expires_at

        if time.time() > client.token_expires_at:
            print('Token has expired - refreshing...')
            refresh_response = client.refresh_access_token(
                client_id=int(os.getenv('STRAVA_CLIENT_ID', None)),
                client_secret=os.getenv('STRAVA_CLIENT_SECRET', None),
                refresh_token=client.refresh_token
            )

            with open('/tmp/strava_auth.json', 'w') as outfile:
                json.dump(refresh_response, outfile)

            self.s3_file_manager.upload_file('/tmp/strava_auth.json', 'strava_auth.json')

        return client

    def get_workout_to_process_file_path(self):
        files_in_workout_directory = self.s3_file_manager.list_object_keys(self.environment + '/workout-to-process/')
        if len(files_in_workout_directory) > 1:
            raise Exception('Only 1 workout should exist in workout-to-process directory. Got: ', files_in_workout_directory)
        if len(files_in_workout_directory) is 0:
            print('No Workouts found to process')
            return None

        return files_in_workout_directory[0]

    def get_workout_id(self, workout_file_path):
        return self.get_workout_base_name(workout_file_path).replace('.tcx', '')

    def get_workout_base_name(self, workout_file_path):
        return workout_file_path.replace(self.workout_to_process_dir, '')

    def move_workout_to_archive(self, workout_to_process_file_path):
        print('Moving workout to archive...')
        self.s3_file_manager.move_object(workout_to_process_file_path, self.get_workout_to_archive_file_path(workout_to_process_file_path))

    def get_workout_to_archive_file_path(self, workout_to_process_file_path):
        return workout_to_process_file_path.replace(self.workout_to_process_dir, self.workout_archive_dir)

    def upload_workout(self, workout_file_path):
        temp_workout_file_path = '/tmp/' + self.get_workout_base_name(workout_file_path)
        self.s3_file_manager.download_file(workout_file_path, temp_workout_file_path)
        self.client.upload_activity(open(temp_workout_file_path), 'tcx', external_id=self.get_workout_id(workout_file_path))
