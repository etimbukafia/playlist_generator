from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
import os
from playlist_create import create_playlist

class Scheduler():
    '''
    This class contains functions for generating playlists based on different subscription plans

    Base plan: Generates a playlist every morning at 10:00 for the user
    Pro plan: Generates three playlists per day at 10:00, 14:00, and 20:00 for the user.
    '''

    def __init__(self, spotify_client, frequency='one'):
        """
        Initializes the Scheduler with a Spotify client for API interactions
        """
        self.spotify_client = spotify_client
        self.frequency = frequency
        self.running = True  # Flag to control scheduler
        self.scheduler = BackgroundScheduler()

    def process_file(self, file_path):
        try:
            if os.path.isfile(file_path):
                with open(file_path, "r") as bio_file:
                    content = bio_file.read().strip()
                    if not content:
                        logging.warning("User music taste file is empty")
                        return
                    logging.info(f"Processing file {file_path}")
                    create_playlist(content, self.spotify_client)
            else:
                logging.error(f"File does not exist: {file_path}")
        except PermissionError:
            logging.error(f"Permission denied: {file_path}")
        except Exception as e:
            logging.error(f"Error processing file: {e}")

    def frequency_once(self):
        '''
        Generates one playlist every morning at 10:00
        '''
        bio_path = r"C:/Users/j/.vscode/match-spotify/playlist_gen/bio.txt"
        self.process_file(bio_path)

    def frequency_thrice(self):
        '''
        Generates three playlists a day: morning, afternoon, evening
        '''
        bio_path = r"C:/Users/j/.vscode/match-spotify/playlist_gen/bio.txt"
        self.process_file(bio_path)

    def start(self):
        '''
        Starts the scheduler
        '''
        logging.info("Starting scheduler...")
        if self.frequency == 'one':
            self.scheduler.add_job(self.base_plan, CronTrigger(hour=22, minute=45))
        elif self.frequency == 'three':
            self.scheduler.add_job(self.pro_plan, CronTrigger(hour=10, minute=0))
            self.scheduler.add_job(self.pro_plan, CronTrigger(hour=14, minute=0))
            self.scheduler.add_job(self.pro_plan, CronTrigger(hour=20, minute=0))
        else:
            logging.error(f"Unknown frequency: {self.frequency}")
            return
        
        self.scheduler.start()

    def stop(self):
        """
        Stops the scheduler gracefully.
        """
        logging.info("Stopping scheduler...")
        self.scheduler.shutdown(wait=True)


