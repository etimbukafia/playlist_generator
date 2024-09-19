import logging
import argparse
from spotify_auth import SpotifyAuthManager
from schedule_logic import Scheduler
from filewatcher import Handler
from watchdog.observers import Observer
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_scheduler(spotify_client):
    scheduler = Scheduler(spotify_client)
    scheduler.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Shutting down scheduler...")
        scheduler.stop()

def run_file_watcher(spotify_client):
    path = r"C:/Users/j/.vscode/match-spotify/playlist_gen/src/"
    event_handler = Handler(spotify_client)
    observer = Observer()
    observer.schedule(event_handler, path=path, recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Stopping file watcher...")
        observer.stop()

    observer.join()

def main():
    try:
        # Argument parser for selecting logic mode
        parser = argparse.ArgumentParser(description="Choose which logic to run: scheduling or file watching")
        parser.add_argument('--mode', type=str, choices=['scheduler', 'file_watcher'], required=True, 
                            help="Select between 'scheduler' or 'file_watcher' mode")
        
        args = parser.parse_args()

        # Initialize the Spotify Auth Manager and get the Spotify client
        manager = SpotifyAuthManager()
        spotify_client = manager.get_spotify_client(manager.flask_app_instance.authorization_code)

        # Running the selected mode
        if args.mode == 'scheduler':
            run_scheduler(spotify_client)
        elif args.mode == 'file_watcher':
            run_file_watcher(spotify_client)
    
    except Exception as e:
        print(f"An error occurred: {e}")
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
