import time
import os
import glob
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

download_directory = os.getcwd() + '/downloads/'
workout_directory = os.getcwd() + '/workout_to_upload/'
archive_directory = os.getcwd() + '/archive/'
request_wait_time = 5


def get_driver():
    options = webdriver.ChromeOptions()
    options.add_experimental_option('prefs', {
        'download.default_directory': download_directory,
        'download.prompt_for_download': False,
        'download.directory_upgrade': True,
        'safebrowsing.enabled': True
    })
    return webdriver.Chrome(options=options)


def login(driver):
    set_gdpr_cookies(driver)
    login_via_form(driver)


def set_gdpr_cookies(driver):
    driver.get('https://www.mapmyrun.com/auth/login/')
    driver.add_cookie({'name': 'notice_behavior', 'value': 'expressed,eu'})
    driver.add_cookie({'name': 'notice_gdpr_prefs', 'value': '0,1,2:'})
    driver.add_cookie({'name': 'notice_preferences', 'value': '2:'})


def login_via_form(driver):
    email_field = driver.find_element_by_css_selector('input#email')
    email_field.send_keys(os.getenv('EMAIL'))
    password_field = driver.find_element_by_css_selector('input#password')
    password_field.send_keys(os.getenv('PASSWORD'))
    password_field.send_keys(Keys.RETURN)
    time.sleep(request_wait_time)


def download_most_recent_workout(driver):
    driver.get('https://www.mapmyrun.com/workouts/')
    workout_box = driver.find_elements_by_css_selector('a[href^="/workout/"].box_title')
    workout_id = workout_box[0].get_attribute("href").replace('https://www.mapmyrun.com/workout/', '')
    print('Latest workout id is: ' + workout_id)
    check_workout_not_already_processed(driver, workout_id)
    download_workout(driver, workout_id)


def check_workout_not_already_processed(driver, workout_id):
    if os.path.exists(workout_directory + workout_id + '.tcx') or os.path.exists(archive_directory + workout_id + '.tcx'):
        driver.close()
        raise Exception('File already processed')


def download_workout(driver, workout_id):
    driver.get('https://www.mapmyrun.com/workout/' + workout_id)
    driver.find_element_by_id('export_to_tcx').click()
    print('Downloaded workout ' + workout_id)
    time.sleep(request_wait_time)
    rename_download(workout_id)


def rename_download(workout_id):
    files_in_downloads = glob.glob(download_directory + '/*')
    if len(files_in_downloads) is not 1:
        raise Exception('Expected a single file in the downloads. Got:', files_in_downloads)
    os.rename(download_directory + files_in_downloads[0], workout_directory + workout_id + '.tcx')


def main():
    driver = get_driver()
    login(driver)
    download_most_recent_workout(driver)
    driver.close()


if __name__ == "__main__":
    main()
