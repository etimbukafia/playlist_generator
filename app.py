import base64
import json
import os
import spotipy
import streamlit as st
import requests
from requests import post
import openai
from dotenv import load_dotenv

load_dotenv()
from spotipy.oauth2 import SpotifyOAuth

client_id = os.environ['PLAYLIST-GENERATOR-CLIENT-ID']
client_secret = os.environ['PLAYLIST-GENERATOR-CLIENT_SECRET']
redirect_uri = "http://localhost:8501"

sp_oauth = SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope='user-library-read playlist-modify-private')

def get_token(authorization_code):
    token_info = sp_oauth.get_access_token(authorization_code)
    return token_info['access_token']

@st.cache_data
def get_spotify_client(authorization_code):
    # Get the access token
    access_token = get_token(authorization_code)
    # Create a Spotipy client
    spotify_client = spotipy.Spotify(auth=access_token)
    return spotify_client

def main():
    client = openai.OpenAI(
    base_url="https://api.fireworks.ai/inference/v1",
    api_key=os.getenv('FIREWORKS_API_KEY')
    )
    if "code" not in st.query_params:
        # If the authorization code is not present in the URL, display a message asking the user to log in
        st.write(
            f"Please log in to <a target='_self' href='{sp_oauth.get_authorize_url()}'>Spotify</a>",
            unsafe_allow_html=True
        )
        return    
    authorization_code = st.query_params["code"]
    spotify_client = get_spotify_client(authorization_code)

    with st.form("Playlist Generation"):
        prompt = st.text_input("Describe the music you want to hear..")
        song_count = st.slider("Songs", 1, 30, 10)
        submitted = st.form_submit_button("Create")
    if not submitted:
        return
    
    messages=[
        {"role": "system", "content": "You are MusicGPT, world's best music recommendation AI. Given a description of a user's music preference, you will recommend songs tailored to the user's preference."},
        {"role": "user", "content": f"Create a playlist with {song_count} songs that fits the following description: '''{prompt}'''. Come up with a creative and unique name for the playlist."},
    ] 

    tools = [
        {
            "type": "function",
            "function": 
            {
                "name": "create_playlist",
                "description": "Creates a Spotify playlist based on a list of songs that should be added to the list",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "playlist_name": {
                            "type": "string",
                            "description": "Name of the playlist",
                        },
                        "playlist_description": {
                            "type": "string",
                            "description": "Description for the playlist",
                        },
                        "songs": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "songname": {
                                        "type": "string",
                                        "description": "Name of the song that should be added to the playlist",
                                    },
                                    "artists": {
                                        "type": "array",
                                        "description": "List of all artists",
                                        "items": {
                                            "type": "string",
                                            "description": "Name of artist of the song",
                                        },
                                    },
                                },
                                "required": ["songname", "artists"],
                            },
                        },
                    },
                    "required": ["songs", "playlist_name", "playlist_description"],
                },
            },
        }
    ]
    
    with st.spinner("Creating playlist..."):
        chat_completion = client.chat.completions.create(
        model="accounts/fireworks/models/firefunction-v1",
        messages=messages,
        tools=tools,
        temperature=0.1
        )

    function_call = chat_completion.choices[0].message.tool_calls[0].function

    arguments = json.loads(function_call.arguments) 
    playlist_name = arguments["playlist_name"]
    playlist_description = arguments["playlist_description"]
    recommended_songs = arguments["songs"]

    song_uris = [
        spotify_client.search(
            q=f"{song['songname']} {','.join(song['artists'])}", limit=1
        )["tracks"]["items"][0]["uri"]
        for song in recommended_songs
    ]

    user_id = spotify_client.me()["id"]
    playlist = spotify_client.user_playlist_create(
        user_id, playlist_name, False, description=playlist_description
    )
    playlist_id = playlist["id"]
    spotify_client.playlist_add_items(playlist_id, song_uris)

    st.write(
        f"Playlist created <a href='{playlist['external_urls']['spotify']}'>Click here to view the playlist</a>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()