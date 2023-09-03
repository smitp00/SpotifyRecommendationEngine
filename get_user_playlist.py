import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Initialize Spotify API with Client Credentials
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="YOUR_CLIENT_ID", client_secret="YOUR_CLIENT_SECRET"))

def get_playlist_tracks(playlist_id):
    """Fetch songs from a given playlist."""
    songs = []
    offset = 0
    limit = 100  # The maximum limit is 100
    
    while True:
        results = sp.playlist_tracks(playlist_id, offset=offset, limit=limit)
        if not results['items']:
            break
        songs.extend(results['items'])
        offset += limit
    
    return songs

def get_audio_features_for_tracks(track_ids):
    """Fetch audio features for a list of track IDs."""
    features_list = []
    for i in range(0, len(track_ids), 100):
        batch = track_ids[i:i + 100]
        audio_features = sp.audio_features(batch)
        features_list.extend(audio_features)
    
    return features_list

if __name__ == '__main__':
    playlist_id = input("Enter the Spotify Playlist URI: ")
    
    # Fetch tracks from the playlist
    playlist_tracks = get_playlist_tracks(playlist_id)
    
    # Extract track IDs
    track_ids = [track['track']['id'] for track in playlist_tracks]
    
    # Fetch audio features for all track IDs
    audio_features = get_audio_features_for_tracks(track_ids)
    
    # Display audio features
    for i, features in enumerate(audio_features):
        print(f"Song: {playlist_tracks[i]['track']['name']}")
        print(f"  - Danceability: {features['danceability']}")
        print(f"  - Energy: {features['energy']}")
        print(f"  - Tempo: {features['tempo']}")
        print(f"  - Acousticness: {features['acousticness']}")
        print(f"  - Instrumentalness: {features['instrumentalness']}")
        print(f"  - Valence: {features['valence']}")