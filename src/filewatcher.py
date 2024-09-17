import watchdog.events
import watchdog.observers
import time, logging
from playlist_create import create_playlist

class Handler(watchdog.events.PatternMatchingEventHandler):

    def __init__(self, spotify_client):
        """
        The __init__ method initializes a class instance designed to monitor changes to a bio.txt 
        using watchdog. It prepares the class to handle file events, initializes an object for 
        Spotify API interactions (spotify_client), and sets up an attribute (last_content) to keep 
        track of the previous content of bio.txt for comparison purposes.
        """
        super().__init__(patterns=['bio.txt'], ignore_directories=True, case_sensitive=False)
        self.spotify_client = spotify_client
        self.last_content = None

    def on_created(self, event):
        """
        - on_created: method defined to handle the "created" event. 
        This method is invoked when a new file is created in the directory being monitored.

        - event: object that contains information about the file system event. 
        - src_path: provides the path of the file or directory that triggered the event.
        - process_file: method defined elsewhere in the class. It’s intended to process bio.txt.
        """
        logging.info("Watchdog received created event - {event.src_path}")
        self.process_file(event.src_path)
          
    def on_modified(self, event):
        logging.info("Watchdog received modified event - {event.src_path}")
        self.process_file(event.src_path)
        

    def process_file(self, file_path):
        try:
            with open(file_path, "r") as bio_file:
                content = bio_file.read().strip()
                if not content:
                    logging.warning(f"File {file_path} is empty. Waiting for content")
                    return
                
                if content == self.last_content:
                    logging.info(f"No changes in file {file_path} since the last processing")
                    return
                
                self.last_content = content
                logging.info(f"processing file {file_path}")
                #Debounce mechanism: wait for a short period to ensure the file is fully saved
                time.sleep(1)
                create_playlist(content, self.spotify_client)
        except FileNotFoundError:
            logging.warning(f"File not found: {file_path}, waiting for the file to be created")
        except Exception as e:
            logging.error(f"Error processing file: {e}")



