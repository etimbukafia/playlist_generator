import logging
import json
import openai
import os
from dotenv import load_dotenv
load_dotenv()

def create_playlist(prompt, spotify_client):
    client = openai.OpenAI(
    base_url="https://api.fireworks.ai/inference/v1",
    api_key=os.getenv('FIREWORKS_API_KEY')
    )

    song_count = 15

    logging.info("Creating playlist...")
    
    messages=[
    {"role": "system", "content": "You are VibeCheck, a highly sophisticated music recommendation AI. Given a detailed description of a user's preferences, you will create personalized playlists that perfectly match their tastes, prioritizing newer music while also incorporating timeless classics."},
    {"role": "user", "content": f"Generate a playlist of {song_count} songs that align with the following description: '''{prompt}'''. Ensure the playlist is diverse, well-curated, and has a creative, memorable name. Prioritize newer music, but also include some timeless classics to create a well-rounded listening experience."}
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

    try:  
        chat_completion = client.chat.completions.create(
        model="accounts/fireworks/models/firefunction-v1",
        messages=messages,
        tools=tools,
        temperature=0.7
        )

        logging.info("Chat completion response received")

        #st.write(chat_completion)

        #if not chat_completion.choices or not chat_completion.choices[0].message.tool_calls:
        #    st.write("Failed to get a valid response from the chat completion.")
        #    return

        function_call = chat_completion.choices[0].message.tool_calls[0].function

        arguments = json.loads(function_call.arguments) 
        playlist_name = arguments["playlist_name"]
        playlist_description = arguments["playlist_description"]
        recommended_songs = arguments["songs"]

        song_uris = []
        for song in recommended_songs:
            search_result = spotify_client.search(q=f"{song['songname']} {','.join(song['artists'])}", limit=1)
            if search_result["tracks"]["items"]:
                song_uris.append(search_result["tracks"]["items"][0]["uri"])
            else:
                logging.warning(f"Song '{song['songname']}' by {', '.join(song['artists'])} not found on Spotify.")

        user_id = spotify_client.me()["id"]
        playlist = spotify_client.user_playlist_create(
            user_id, playlist_name, False, description=playlist_description
        )
        playlist_id = playlist["id"]
        spotify_client.playlist_add_items(playlist_id, song_uris)

        logging.info(f"Playlist created: {playlist['external_urls']['spotify']}")
    except Exception as e:
        logging.error(f"Error creating playlist: {e}")