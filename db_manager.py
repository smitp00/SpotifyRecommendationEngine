import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import psycopg2
from urllib.parse import urlparse
import config  # import config.py


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
        ), conn.cursor()

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

    return conn, conn.cursor()


def close_database(conn, cur):
    cur.close()
    conn.close()


def clear_songs_table(cur, conn):
    cur.execute("TRUNCATE TABLE songs;")
    conn.commit()


def remove_duplicates(cur, conn):
    cur.execute("""
    DELETE FROM songs
    WHERE id NOT IN (
       SELECT MIN(id)
        FROM songs
        GROUP BY name
    );
    """)
    conn.commit()


def fetch_latest_songs(cur, limit=1000):
    cur.execute(f"SELECT * FROM songs ORDER BY id DESC LIMIT {limit};")
    return cur.fetchall()


def get_total_song_count(cur):
    cur.execute("SELECT COUNT(*) FROM songs;")
    return cur.fetchone()[0]


def get_unique_song_count_by_name(cur):
    cur.execute("SELECT COUNT(DISTINCT name) FROM songs;")
    return cur.fetchone()[0]


if __name__ == "__main__":
    conn, cur = connect_to_database()

    # Uncomment the next line if you want to clear the song table:
    # clear_songs_table(cur, conn)

    # Uncomment next line to remove duplicates
    # remove_duplicates(cur, conn)

    latest_songs = fetch_latest_songs(cur)
    for song in latest_songs:
        print(f"ID: {song[0]}, Name: {song[1]}, Artist: {song[2]}, Danceability: {song[3]}, Energy: {song[4]}, Tempo: {song[5]}, Acousticness: {song[6]}, Instrumentalness: {song[7]}, Valence: {song[8]}")

    total_songs = get_total_song_count(cur)
    print(f"The total number of songs in the database is: {total_songs}")

    unique_songs = get_unique_song_count_by_name(cur)
    print(f"There are {unique_songs} unique songs by name in the database.")

    close_database(conn, cur)