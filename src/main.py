import logging
from spotify_auth import SpotifyAuthManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    try:
        manager = SpotifyAuthManager()
        manager.initialize_and_monitor_bio()
    except Exception as e:
        print(f"An error occured: {e}")
        logging.error(f"An error occured: {e}")

if __name__ == "__main__":
    main()