from schedule import every, repeat
import time
import logging
import schedule
from playlist_create import create_playlist
import os

class Scheduler():
    '''
    This class contains functions for generating playlists based on different subscrition plans

    Base plan: Generates a playlist every morning at 10:00 for user
    Pro plan: Generates three playlists for per day at 10:00, 14:00, and 20:00 for the user.

    NOTE: EXPLORE OTHER ADVANCED SCHEDULERS LATER
    '''

    def __init__(self, spotify_client, plan='base'):
        """
        Initializes the Scheduler with a Spotify client for API interactions
        """
        self.spotify_client = spotify_client
        self.plan = plan
        self.running = True  # Flag to control scheduler

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

    def base_plan(self):
        '''
        Schedule function for the base plan. 
        Generates one playlist every morning at 10:00
        '''
        bio_path = r"C:/Users/j/.vscode/match-spotify/playlist_gen/bio.txt"
        self.process_file(bio_path)

    def pro_plan(self):
        '''
        Schedule function for the pro plan
        Generates three playlists a day: morning, afternoon, evening
        '''
        bio_path = r"C:/Users/j/.vscode/match-spotify/playlist_gen/bio.txt"
        self.process_file(bio_path)

    
    def start(self):
        '''
        Starts the scheduler
        start method to handle running all scheduled tasks in an infinite loop, continuously checking for any pending jobs to run.
        '''
        logging.info("Starting scheduler...")
        if self.plan == 'base':
            schedule.every().day.at("22:55").do(self.base_plan)
        elif self.plan == 'pro':
            schedule.every().day.at("10:00").do(self.pro_plan)
            schedule.every().day.at("14:00").do(self.pro_plan)
            schedule.every().day.at("20:00").do(self.pro_plan)
        else:
            logging.error(f"unknown plan: {self.plan}")
            return
        
        while self.running:
            schedule.run_pending()  #loop to execute any pending scheduled jobs.
            time.sleep(1)

    
    def stop(self):
        """
        Stops the scheduler gracefully.
        """
        logging.info("Stopping scheduler...")
        self.running = False

