from stravalib.client import Client
import time
import os
import json
import glob

workout_directory = os.getcwd() + '/workout_to_upload'
archive_directory = os.getcwd() + '/archive'


def create_client():
    with open('strava_auth.json') as auth_json:
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

        with open('strava_auth.json', 'w') as outfile:
            json.dump(refresh_response, outfile)

    return client


def get_most_recent_workout_file_path():
    files_in_workout_directory = glob.glob(workout_directory + '/*')
    if len(files_in_workout_directory) is not 1:
        raise Exception('Only 1 workout should exist in upload directory. Got: ', files_in_workout_directory)
    return files_in_workout_directory[0]


def get_workout_id(workout_file_path):
    return os.path.basename(workout_file_path).replace('.tcx', '')


def move_workout_to_archive(workout_file_path):
    os.rename(workout_file_path, archive_directory + '/' + os.path.basename(workout_file_path))


def upload_workout(client, workout_file_path):
    client.upload_activity(open(workout_file_path), 'tcx', external_id=get_workout_id(workout_file_path))


def main():
    client = create_client()
    workout_file_path = get_most_recent_workout_file_path()
    print('About to upload workout: ' + get_workout_id(workout_file_path))
    upload_workout(client, workout_file_path)
    print('Workout uploaded to Strava!')
    move_workout_to_archive(workout_file_path)


if __name__ == "__main__":
    main()
