import psycopg2
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from sklearn.metrics.pairwise import cosine_similarity
import config  # Assuming you've created a config.py to store credentials, like before

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=config.SPOTIFY_CLIENT_ID, client_secret=config.SPOTIFY_CLIENT_SECRET))


def connect_to_database():
    conn = psycopg2.connect(
        host=config.DB_HOST,
        database=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        port=config.DB_PORT
    )
    return conn, conn.cursor()


def fetch_all_songs(cur):
    cur.execute("SELECT * FROM songs")
    return pd.DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])


def get_playlist_data(playlist_id):
    songs = []
    offset = 0
    limit = 100
    
    # First call to get the metadata of the playlist
    playlist_metadata = sp.playlist(playlist_id)
    
    # Extract the playlist name and total number of songs
    playlist_name = playlist_metadata['name']
    total_songs = playlist_metadata['tracks']['total']
    
    while True:
        results = sp.playlist_tracks(playlist_id, offset=offset, limit=limit)
        if not results['items']:
            break
        songs.extend(results['items'])
        offset += limit
    
    return songs, playlist_name, total_songs



def get_audio_features_for_tracks(track_ids):
    features_list = []
    for i in range(0, len(track_ids), 100):
        batch = track_ids[i:i + 100]
        audio_features = sp.audio_features(batch)
        features_list.extend(audio_features)
    
    return features_list


def recommend_knn_euclidean(df, knn_df, playlist_knn_df):
    scaler = StandardScaler()
    knn_df_scaled = scaler.fit_transform(knn_df)
    centroid = scaler.transform([playlist_knn_df.mean(axis=0)])
    
    knn = NearestNeighbors(n_neighbors=10)
    knn.fit(knn_df_scaled)
    distances, indices = knn.kneighbors(centroid)
    
    return df.iloc[indices[0]]


def recommend_cosine_similarity(df, knn_df, playlist_knn_df):
    scaler = StandardScaler()
    knn_df_scaled = scaler.fit_transform(knn_df)
    centroid = scaler.transform([playlist_knn_df.mean(axis=0)])
    
    similarity_matrix = cosine_similarity(centroid, knn_df_scaled)
    similarity_series = pd.Series(similarity_matrix[0])
    top_10_indices = similarity_series.sort_values(ascending=False).head(10).index
    
    return df.iloc[top_10_indices]


def get_recommendations(playlist_input):
    conn, cur = connect_to_database()
    db_df = fetch_all_songs(cur)
    cur.close()
    conn.close()
    
    playlist_id = playlist_input.split(':')[-1] if 'spotify:playlist:' in playlist_input else playlist_input
    playlist_tracks, playlist_name, total_songs = get_playlist_data(playlist_id)
    
    track_ids = [track['track']['id'] for track in playlist_tracks]
    audio_features = get_audio_features_for_tracks(track_ids)
    playlist_df = pd.DataFrame(audio_features)
    playlist_knn_df = playlist_df[['danceability', 'energy', 'tempo', 'acousticness', 'instrumentalness', 'valence']]
    knn_df = db_df[['danceability', 'energy', 'tempo', 'acousticness', 'instrumentalness', 'valence']]
    
    recommended_songs_knn = recommend_knn_euclidean(db_df, knn_df, playlist_knn_df)
    
    recommended_songs_cosine = recommend_cosine_similarity(db_df, knn_df, playlist_knn_df)
    
    return recommended_songs_knn, recommended_songs_cosine, playlist_name, total_songs



if __name__ == '__main__':
    playlist_input = input("Enter the Spotify Playlist URI or ID or HTTPS (website of playlist): ")
    recommended_songs_knn, recommended_songs_cosine, playlist_name, total_songs = get_recommendations(playlist_input)

    print(f"Playlist: {playlist_name}")
    print(f"Total songs in the playlist: {total_songs}")
    print("\nBased on K-NN using Euclidean Distance, here are 10 recommended songs:")
    print(recommended_songs_knn[['name', 'artist','danceability', 'energy', 'tempo', 'acousticness', 'instrumentalness', 'valence']])
    
    print("\n\nBased on Direct Cosine Similarity, here are 10 recommended songs:")
    print(recommended_songs_cosine[['name', 'artist','danceability', 'energy', 'tempo', 'acousticness', 'instrumentalness', 'valence']])