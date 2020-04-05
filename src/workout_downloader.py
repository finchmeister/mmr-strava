import time
import os
import glob
from selenium.webdriver.common.keys import Keys


class WorkoutDownloader:

    request_wait_time = 5

    def __init__(self, s3_file_manager, download_directory):
        self.s3_file_manager = s3_file_manager
        self.download_directory = download_directory
        self.environment = os.getenv('ENVIRONMENT')

    def main(self, driver):
        self.login(driver)
        self.download_most_recent_workout(driver)

    def login(self, driver):
        self.set_gdpr_cookies(driver)
        self.login_via_form(driver)

    def set_gdpr_cookies(self, driver):
        print('Logging In...')
        driver.get('https://www.mapmyrun.com/auth/login/')
        driver.add_cookie({'name': 'notice_behavior', 'value': 'expressed,eu'})
        driver.add_cookie({'name': 'notice_gdpr_prefs', 'value': '0,1,2:'})
        driver.add_cookie({'name': 'notice_preferences', 'value': '2:'})

    def login_via_form(self, driver):
        email_field = driver.find_element_by_css_selector('input#email')
        email_field.send_keys(os.getenv('MMR_EMAIL'))
        password_field = driver.find_element_by_css_selector('input#password')
        password_field.send_keys(os.getenv('MMR_PASSWORD'))
        password_field.send_keys(Keys.RETURN)
        time.sleep(self.request_wait_time)
        print('Logged In: ' + driver.current_url)

    def download_most_recent_workout(self, driver):
        driver.get('https://www.mapmyrun.com/workouts/')
        print('Finding latest workout from: ' + driver.current_url)
        workout_box = driver.find_elements_by_css_selector('a[href^="/workout/"].box_title')
        workout_id = workout_box[0].get_attribute("href").replace('https://www.mapmyrun.com/workout/', '')
        print('Latest workout id is: ' + workout_id)
        if self.has_workout_already_been_processed(driver, workout_id):
            return
        self.download_workout(driver, workout_id)

    def has_workout_already_been_processed(self, driver, workout_id):
        print('Checking if workout has already been processed...')
        if self.s3_file_manager.file_exists(self.get_workout_to_process_path(workout_id)):
            driver.close()
            print('File found in "workout-to-process" folder')
            return True

        if self.s3_file_manager.file_exists(self.get_workout_to_archive_path(workout_id)):
            driver.close()
            print('File found in "archive" folder')
            return True

        return False

    def download_workout(self, driver, workout_id):
        driver.get('https://www.mapmyrun.com/workout/' + workout_id)
        driver.find_element_by_id('export_to_tcx').click()
        time.sleep(self.request_wait_time)
        print('Downloaded workout: ' + workout_id)
        self.upload_to_s3(workout_id)

    def upload_to_s3(self, workout_id):
        files_in_downloads = glob.glob(self.download_directory + '/*.tcx')
        print(files_in_downloads)
        if len(files_in_downloads) is not 1:
            raise Exception('Expected a single .tcx file in the downloads. Got:', files_in_downloads)
        get_workout_upload_path = self.get_workout_to_process_path(workout_id)
        print('Uploading to S3: ' + get_workout_upload_path)
        self.s3_file_manager.upload_file(files_in_downloads[0], get_workout_upload_path)

    def get_workout_to_process_path(self, workout_id):
        return self.environment + '/workout-to-process/' + workout_id + '.tcx'

    def get_workout_to_archive_path(self, workout_id):
        return self.environment + '/archive/' + workout_id + '.tcx'
