# playlist_generator
This is a Python-based application that interacts with the Spotify API to generate customized playlists based on user preferences. The application offers two modes: scheduling playlists at specific times or monitoring a file to create playlists in response to changes in a txt file, called 'bio.txt'. The content of this bio.txt serves as the prompt.

# Features
- Scheduler Mode: Automatically generates playlists at scheduled times (e.g., every morning at 10:00 AM). 
- File Watcher Mode: Monitors changes to the bio.txt file and generates a new playlist whenever the file is updated.

# Installation
Clone the respository:
```bash
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
```

Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # For Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a .env file in the root directory and add your Spotify API credentials:
```objectivec
PLAYLIST-GENERATOR-CLIENT-ID=your_spotify_client_id
PLAYLIST-GENERATOR-CLIENT_SECRET=your_spotify_client_secret
```

Set up Flask for Spotify OAuth:
In the "spotify_auth.py" file, Flask is used to manage the OAuth process. Ensure that Flask runs correctly on "http://localhost:5000/callback".

# Usage
To start the application in Scheduler Mode, run:
```bash
python main.py --mode scheduler
```

To start the application in File Watcher Mode, run:
```bash
python main.py --mode file_watcher
```


