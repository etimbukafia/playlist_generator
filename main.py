import os
import spotipy
from requests import post
from dotenv import load_dotenv
import time
import threading
from flask import Flask, request
import logging
from filewatcher import Handler
import watchdog.observers
load_dotenv()
from spotipy.oauth2 import SpotifyOAuth

client_id = os.environ['PLAYLIST-GENERATOR-CLIENT-ID']
client_secret = os.environ['PLAYLIST-GENERATOR-CLIENT_SECRET']

redirect_uri = "http://localhost:5000/callback"

scopes = ["playlist-modify-public", "playlist-read-collaborative", "playlist-read-private", "user-modify-playback-state", "user-read-private", "user-read-email", "user-read-playback-state", "user-read-recently-played", "user-top-read", "user-library-read", "playlist-modify-private"]

sp_oauth = SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scopes)

app = Flask(__name__)
authorization_code = None

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


@app.route('/callback')
def callback():
    global authorization_code
    authorization_code = request.args.get('code')
    logging.info(f"Authorization code received: {authorization_code}")
    return "Authorization successful! You can close the window."

def get_token(authorization_code):
    try:
        token_info = sp_oauth.get_access_token(authorization_code)
        logging.info(f"token info gotten!: {token_info}")
        return token_info['access_token']
    except Exception as e:
        logging.error(f"Failed to get token: {e}")
        return None

def get_spotify_client(authorization_code):
    # Get the access token
    access_token = get_token(authorization_code)
    # Create a Spotipy client
    spotify_client = spotipy.Spotify(auth=access_token)
    logging.info('spotify client authenticated')
    return spotify_client

def start_flask_app():
    app.run(port=5000, debug=True, use_reloader=False)


def initialize_and_monitor_bio():
    global authorization_code
    threading.Thread(target=start_flask_app).start()
    
    auth_url = sp_oauth.get_authorize_url()
    print(f"please log in to Spotify: {auth_url}") 

    while authorization_code is None:
        time.sleep(1)

    logging.info("Authorization code received, initializing spotify client.... ")
    spotify_client = get_spotify_client(authorization_code)

    bio_path = r"C:/Users/j/.vscode/match-spotify/playlist_gen"
    event_handler = Handler(spotify_client)
    observer = watchdog.observers.Observer()
    observer.schedule(event_handler, path=bio_path, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def main():
    initialize_and_monitor_bio()

if __name__ == "__main__":
    main()