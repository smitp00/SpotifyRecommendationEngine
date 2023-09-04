import psycopg2
import pandas as pd
from collections import Counter
from sklearn.neighbors import NearestNeighbors
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import numpy as np  # Add this line

# Initialize Spotify API
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="c00c74aff95d47ada8bb2b8ee9ed7313", client_secret="d7de766b64964afd8ff56d80c47e67b8"))

# Connect to PostgreSQL database
conn = psycopg2.connect(
    host="localhost",
    database="spotify_database",
    user="smitpatel",
    password="Spate469!-",
    port="5432"
)

# Create a new cursor
cur = conn.cursor()

# Execute SQL query and fetch data into a Pandas DataFrame
cur.execute("SELECT * FROM songs")
db_df = pd.DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])

# Close the cursor and connection
cur.close()
conn.close()

# Prepare DataFrame for k-NN model
knn_df = db_df[['danceability', 'energy', 'tempo', 'acousticness', 'instrumentalness', 'valence']]

# Train k-NN model
knn = NearestNeighbors(n_neighbors=10)
knn.fit(knn_df)

# Print the feature names used during fitting
print("Features used to fit the model:", knn.feature_names_in_)

# Function to get playlist tracks (fetches all playlist songs, 100 at a time)
def get_playlist_tracks(playlist_id):
    songs = []
    offset = 0
    limit = 100
    
    while True:
        results = sp.playlist_tracks(playlist_id, offset=offset, limit=limit)
        if not results['items']:
            break
        songs.extend(results['items'])
        offset += limit
    
    return songs
# Function to get audio features for tracks
def get_audio_features_for_tracks(track_ids):
    features_list = []
    for i in range(0, len(track_ids), 100):
        batch = track_ids[i:i + 100]
        audio_features = sp.audio_features(batch)
        features_list.extend(audio_features)
    
    return features_list

# Main function
if __name__ == '__main__':
    # Get the playlist ID from the user
    playlist_input = input("Enter the Spotify Playlist URI or ID: ")
    
    # Extract the actual playlist ID from the input
    if 'spotify:playlist:' in playlist_input:
        playlist_id = playlist_input.split(':')[-1]
    else:
        playlist_id = playlist_input

    # Fetch the tracks from the given playlist
    playlist_tracks = get_playlist_tracks(playlist_id)
    track_ids = [track['track']['id'] for track in playlist_tracks]
    
    # Fetch audio features for these tracks
    audio_features = get_audio_features_for_tracks(track_ids)
    
    # Convert the list of dictionaries into a Pandas DataFrame
    playlist_df = pd.DataFrame(audio_features)
    
    # Prepare this DataFrame for k-NN (keeping only relevant numerical features)
    playlist_knn_df = playlist_df[['danceability', 'energy', 'tempo', 'acousticness', 'instrumentalness', 'valence']]

    # Make sure the column names match
    playlist_knn_df.columns = knn_df.columns

    # Initialize a list to keep track of all recommendations
    all_recommendations = []

    # Loop through each song in the playlist to find similar songs
    for i, song in enumerate(playlist_tracks):
        distances, indices = knn.kneighbors([playlist_knn_df.iloc[i]])
        all_recommendations.extend(indices[0])

    # Count the occurrences of each recommended song
    song_counter = Counter(all_recommendations)

    # Find the top 10 most commonly recommended songs
    most_common_recommendations = song_counter.most_common(10)
    most_common_indices = [item[0] for item in most_common_recommendations]

    # Fetch these top 10 songs from the database and display them
    top_10_songs = db_df.iloc[most_common_indices]

    print("Top 10 recommended songs based on the entire playlist:")
    print(top_10_songs)

