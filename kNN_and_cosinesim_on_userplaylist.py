import psycopg2
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from sklearn.metrics.pairwise import cosine_similarity

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

print(db_df.columns)

# Don't forget to close the cursor and connection when you're done
cur.close()
conn.close()

# Initialize the MinMaxScaler
scaler = MinMaxScaler() #normalizing


# Prepare for k-NN (only keeping numerical features for the model)
knn_df = db_df[['danceability', 'energy', 'tempo', 'acousticness', 'instrumentalness', 'valence']]
knn_df_scaled = scaler.fit_transform(knn_df) #normalizing

# Train k-NN model on scaled data
knn = NearestNeighbors(n_neighbors=10)
knn.fit(knn_df_scaled)


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

def get_audio_features_for_tracks(track_ids):
    features_list = []
    for i in range(0, len(track_ids), 100):
        batch = track_ids[i:i + 100]
        audio_features = sp.audio_features(batch)
        features_list.extend(audio_features)
    
    return features_list

if __name__ == '__main__':
    playlist_input = input("Enter the Spotify Playlist URI or ID ot HTTPS (website of playlist): ")
    
    if 'spotify:playlist:' in playlist_input:
        playlist_id = playlist_input.split(':')[-1]
    else:
        playlist_id = playlist_input

    playlist_tracks = get_playlist_tracks(playlist_id)
    track_ids = [track['track']['id'] for track in playlist_tracks]
    
    audio_features = get_audio_features_for_tracks(track_ids)

    # Convert audio features to a Pandas DataFrame
    playlist_df = pd.DataFrame(audio_features)
    
    # Prepare DataFrame for k-NN model
    playlist_knn_df = playlist_df[['danceability', 'energy', 'tempo', 'acousticness', 'instrumentalness', 'valence']]
    
    # Initialize scaler
    scaler = StandardScaler()
    knn_df_scaled = scaler.fit_transform(knn_df)  # Assuming knn_df is your training data
    
    # Scale the playlist features
    playlist_knn_df_scaled = scaler.transform(playlist_knn_df)
    
    # Compute the centroid of the playlist for cosine similarity
    centroid = scaler.transform([playlist_knn_df.mean(axis=0)])
    
    # Use k-NN model to find the 10 most similar songs in the database to the "centroid" song
    knn = NearestNeighbors(n_neighbors=10)
    knn.fit(knn_df_scaled)
    distances, indices = knn.kneighbors(centroid)
    
    recommendations = indices[0]
    
    recommended_songs = db_df.iloc[recommendations]

    print("Based on your K-NN using Euclidean Distance, here are 10 recommended songs:")
    print(recommended_songs[['name', 'artist','danceability', 'energy', 'tempo', 'acousticness', 'instrumentalness', 'valence']])
    
    ## COSINE SIMILARITY
    # Compute cosine similarity between the centroid and all songs in the database
    similarity_matrix = cosine_similarity(centroid, knn_df_scaled)
    similarity_series = pd.Series(similarity_matrix[0])
    
    # Get top 10 most similar songs
    top_10_indices = similarity_series.sort_values(ascending=False).head(10).index
    recommended_songs_cosine = db_df.iloc[top_10_indices]

    print("\n\nBased on cosine similarity, here are 10 recommended songs:")
    print(recommended_songs_cosine[['name', 'artist','danceability', 'energy', 'tempo', 'acousticness', 'instrumentalness', 'valence']])