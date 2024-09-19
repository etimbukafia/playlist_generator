import os
import spotipy
from requests import post
from dotenv import load_dotenv
import time
import threading
import logging
from spotipy.oauth2 import SpotifyOAuth
from flask_app import FlaskApp

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SpotifyAuthManager:
    def __init__(self):
        self.client_id = os.environ['PLAYLIST-GENERATOR-CLIENT-ID']
        self.client_secret = os.environ['PLAYLIST-GENERATOR-CLIENT_SECRET']
        self.redirect_uri = "http://localhost:5000/callback"
        self.scopes = [
            "playlist-modify-public", "playlist-read-collaborative", "playlist-read-private",
            "user-modify-playback-state", "user-read-private", "user-read-email",
            "user-read-playback-state", "user-read-recently-played", "user-top-read",
            "user-library-read", "playlist-modify-private"
        ]
        self.sp_oauth = SpotifyOAuth(client_id=self.client_id, client_secret=self.client_secret,
                                     redirect_uri=self.redirect_uri, scope=self.scopes)
        self.authorization_code = None
        self.flask_app_instance = FlaskApp()
        
    def get_token(self, authorization_code):
        try:
            token_info = self.sp_oauth.get_access_token(authorization_code)
            logging.info(f"token info received: {token_info}")
            return token_info['access_token']
        except Exception as e:
            logging.error(f"Failed to get token: {e}")
            return None

    def get_spotify_client(self, authorization_code):
        # Get the access token
        access_token = self.get_token(authorization_code)
        if not access_token:
            raise ValueError("Failed to get access token")
        # Create a Spotipy client
        spotify_client = spotipy.Spotify(auth=access_token)
        logging.info('spotify client authenticated')
        return spotify_client

    def initialize_and_monitor_bio(self):
        threading.Thread(target=self.flask_app_instance.start).start()
        
        auth_url = self.sp_oauth.get_authorize_url()
        print(f"please log in to Spotify: {auth_url}") 

        # Wait for the authorization code with a timeout
        max_retries = 60  # e.g., 60 seconds timeout
        retries = 0
        while self.flask_app_instance.authorization_code is None and retries < max_retries:
            time.sleep(1)
            retries +=1

        if self.flask_app_instance.authorization_code is None:
            logging.error("Failed to receive authorization code in time. Exiting...")
            return  # Exit or handle the error appropriately
    
        self.authorization_code = self.flask_app_instance.authorization_code
        logging.info("Authorization code received, initializing spotify client.... ")
        return self.get_spotify_client(self.authorization_code)