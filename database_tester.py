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

# Execute the SQL query to remove duplicates
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



# Execute SQL query to fetch first 100 songs
cur.execute("SELECT * FROM songs LIMIT 100;")

# Fetch all rows (in this case, first 100)
rows = cur.fetchall()

# Print each row
for row in rows:
    print("ID:", row[0])
    print("Name:", row[1])
    print("Artist:", row[2])
    print("Danceability:", row[3])
    print("Energy:", row[4])
    print("Tempo:", row[5])
    print("Acousticness:", row[6])
    print("Instrumentalness:", row[7])
    print("Valence:", row[8])
    print("-----------")

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