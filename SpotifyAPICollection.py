#pip install spotipy psycopg2-binary
#brew install postgresql
#psql postgres to access the postgresql in main command line, create database, user, password

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import psycopg2


sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="8adbfe1bbb1345bab14433e02f93f630", client_secret="a17511ded02e473884662fc2081b211c"))

conn = psycopg2.connect(
    host="localhost",
    database="spotify_database",
    user="smitpatel",
    password="Spate469!-",
    port="5432"
)


cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS songs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    artist VARCHAR(255),
    danceability FLOAT,
    energy FLOAT,
    tempo FLOAT,
    acousticness FLOAT,
    instrumentalness FLOAT,
    valence FLOAT
);
""") 
conn.commit()

# Initialize variables for pagination
limit = 50  # Number of results per request
total_songs_to_fetch = 1000  # Total number of songs you want to fetch
offset = 0  # Starting index of results

unique_song_ids = set()

while offset < total_songs_to_fetch:
    # Fetch songs from Spotify
    
    track_results = sp.search(q='genre:"country"', type='track', limit=limit, offset=offset)
    
    for i, item in enumerate(track_results['tracks']['items']):
        song_id = item['id']
        
        if song_id in unique_song_ids:
            # Skip this song if it's a duplicate
            continue

        # Mark this song ID as seen
        unique_song_ids.add(song_id)
        
        # Continue as before
        song_name = item['name']
        song_artist = item['artists'][0]['name']
        features = sp.audio_features(song_id)[0]
        
        danceability = features['danceability']
        energy = features['energy']
        tempo = features['tempo']
        acousticness = features['acousticness']
        instrumentalness = features['instrumentalness']
        valence = features['valence']
        
        # Insert song into PostgreSQL database
        cur.execute("""
        INSERT INTO songs (name, artist, danceability, energy, tempo, acousticness, instrumentalness, valence)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """, (song_name, song_artist, danceability, energy, tempo, acousticness, instrumentalness, valence))
    
    # Commit the transaction
    conn.commit()
    
    # Update offset for next iteration
    offset += limit
  
    
#additional test
cur.execute("SELECT COUNT(*) FROM songs;")
count = cur.fetchone()[0]

print(f"The total number of songs in the database is: {count}")
#additional test code^

cur.close()
conn.close()