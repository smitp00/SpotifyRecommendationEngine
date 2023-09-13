import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import psycopg2
import config  # Import configuration 
import os
from urllib.parse import urlparse

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=config.SPOTIFY_CLIENT_ID, client_secret=config.SPOTIFY_CLIENT_SECRET))

def connect_to_database():
    DATABASE_URL = os.environ.get('DATABASE_URL')  # Fetch the DATABASE_URL from the environment

    if not DATABASE_URL:  # If DATABASE_URL is not set (e.g., running locally), fallback to your config
        return psycopg2.connect(
            host=config.DB_HOST,
            database=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            port=config.DB_PORT
        )

    # Parse the DATABASE_URL
    result = urlparse(DATABASE_URL)
    username = result.username
    password = result.password
    database = result.path[1:]
    hostname = result.hostname
    port = result.port

    conn = psycopg2.connect(
        dbname=database,
        user=username,
        password=password,
        host=hostname,
        port=port
    )

    return conn

def create_song_table(conn):
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
    cur.close()

def fetch_and_insert_songs(total_songs_to_fetch=1000, genre="pop", limit=50):
    offset = 0  # Starting index of results
    unique_song_ids = set()

    conn = connect_to_database()
    cur = conn.cursor()

    while offset < total_songs_to_fetch:
        track_results = sp.search(q=f'genre:"{genre}"', type='track', limit=limit, offset=offset) 

        for item in track_results['tracks']['items']:
            song_id = item['id']
            
            if song_id in unique_song_ids:
                continue

            unique_song_ids.add(song_id)
            song_name = item['name']
            song_artist = item['artists'][0]['name']
            features = sp.audio_features(song_id)[0]

            danceability = features['danceability']
            energy = features['energy']
            tempo = features['tempo']
            acousticness = features['acousticness']
            instrumentalness = features['instrumentalness']
            valence = features['valence']

            cur.execute("""
            INSERT INTO songs (name, artist, danceability, energy, tempo, acousticness, instrumentalness, valence)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """, (song_name, song_artist, danceability, energy, tempo, acousticness, instrumentalness, valence))

        conn.commit()
        offset += limit

    cur.close()
    conn.close()

def get_total_song_count():
    conn = connect_to_database()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM songs;")
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count

def get_unique_song_count_by_name():
    conn = connect_to_database()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(DISTINCT name) FROM songs;")
    unique_count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return unique_count

if __name__ == "__main__":
    conn = connect_to_database()
    create_song_table(conn)
    conn.close()
    fetch_and_insert_songs()
    total_songs = get_total_song_count()
    unique_songs = get_unique_song_count_by_name()
    print(f"The total number of songs in the database is: {total_songs}")
    print(f"The total number of unique songs (by name) in the database is: {unique_songs}")
