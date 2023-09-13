from flask import Flask, render_template, request, redirect, url_for
import kNN_and_cosinesim_on_userplaylist as recommender
from spotipy.exceptions import SpotifyException

app = Flask(__name__)

#app.py route activation 
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        playlist_id = request.form['playlist_id']
        try:
            recommended_songs_knn, recommended_songs_cosine, playlist_name, total_songs = recommender.get_recommendations(playlist_id)

        except SpotifyException as e:
            if e.http_status == 404:
                # This means the playlist was not found.
                error_msg = "Invalid Spotify Playlist ID. Please check and try again."
                # Render your template with this error message.
                return render_template('index.html', error=error_msg)
            else:
                # Handle other Spotify exceptions if needed.
                error_msg = "An error occurred while fetching data from Spotify. Please try again later."
                return render_template('index.html', error=error_msg)
        
        # Print out the recommendations to inspect the data:
        print("K-NN Recommendations:\n", recommended_songs_knn)
        print("\nCosine Similarity Recommendations:\n", recommended_songs_cosine)
        print("\nPlaylist name:", playlist_name, " Total Songs:", total_songs)

        #returns results.html only if no errors with playlist ID
        return render_template('results.html', songs_knn=recommended_songs_knn, songs_cosine=recommended_songs_cosine, playlist_name=playlist_name, total_songs=total_songs)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)