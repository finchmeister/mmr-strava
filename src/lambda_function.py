from src.webdriver_wrapper import WebDriverWrapper
from src.workout_downloader import WorkoutDownloader
from src.s3_file_manger import S3FileManager
from src.strava_importer import StravaImporter


def lambda_handler(*args, **kwargs):
    s3_file_manager = S3FileManager()
    driver_wrapper = WebDriverWrapper('/tmp/downloads')
    driver = driver_wrapper.get_driver()
    workout_downloader = WorkoutDownloader(s3_file_manager, '/tmp/downloads')
    workout_downloader.main(driver)
    strava_importer = StravaImporter(s3_file_manager)
    strava_importer.main()
