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
conn.commit()


#un-comment out next two lines to clear table
#cur.execute("TRUNCATE TABLE songs;")
#conn.commit()

#Execute the SQL query to remove duplicates
#cur.execute("""
#DELETE FROM songs
#WHERE id NOT IN (
#   SELECT MIN(id)
#    FROM songs
#    GROUP BY name
#);
#""")

# Commit the changes
conn.commit()


# Fetch and Print 1000 Latest Songs
cur.execute("SELECT * FROM songs ORDER BY id DESC LIMIT 1000;")
latest_songs = cur.fetchall()

# Printing the latest 1000 songs
for song in latest_songs:
    print(f"ID: {song[0]}, Name: {song[1]}, Artist: {song[2]}, Danceability: {song[3]}, Energy: {song[4]}, Tempo: {song[5]}, Acousticness: {song[6]}, Instrumentalness: {song[7]}, Valence: {song[8]}")


#print total number of songs
cur.execute("SELECT COUNT(*) FROM songs;")
count = cur.fetchone()[0]
print(f"The total number of songs in the database is: {count}")

# Execute the SQL query to find unique song names
cur.execute("SELECT COUNT(DISTINCT name) FROM songs;")
count = cur.fetchone()[0]
print(f"There are {count} unique songs by name in the database.")




#close database connection
cur.close()
conn.close()