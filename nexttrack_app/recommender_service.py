import os
import joblib
import numpy as np
from django.conf import settings
from .models import Track

class MusicRecommender:
    def __init__(self):
        # Define paths to assets in ml_assets/
        assets_path = os.path.join(settings.BASE_DIR, 'ml_assets')
        
        # Load the joblib files into memory once （loaded when the server starts）
        try:
            self.model = joblib.load(os.path.join(assets_path, 'music_recommender_model.joblib'))
            self.scaler = joblib.load(os.path.join(assets_path, 'scaler.joblib'))
            self.id_map = joblib.load(os.path.join(assets_path, 'model_track_ids.joblib'))
            print("--- ML Engine: Successfully loaded models and ID maps ---")
        except Exception as e:
            print(f"--- ML Engine Error: Could not load assets. {e} ---")

    def get_candidate_pool(self, seed_track_id, n_candidates=150):
        """
        Takes a track_id and returns a large pool of similar Spotify IDs.
        Does NOT filter yet; just gives the raw ML results.
        """
        try:
            # Fetch the seed song's features from the database
            target_track = Track.objects.get(track_id=seed_track_id)
            
            # Prepare the numerical features in the exact order used during training
            features = np.array([[
                target_track.danceability, target_track.energy, target_track.valence,
                target_track.acousticness, target_track.instrumentalness,
                target_track.speechiness, target_track.liveness, target_track.loudness,
                target_track.tempo, target_track.key, target_track.mode
            ]])

            # Scale the features
            scaled_features = self.scaler.transform(features)

            # Query the KNN model for 150 neighbors 
            distances, indices = self.model.kneighbors(scaled_features, n_neighbors=n_candidates)

            # Map the indices to Track IDs using the saved map
            # [0][1:] skips the first index (the seed song)
            neighbor_indices = indices[0][1:]
            candidate_ids = self.id_map[neighbor_indices]

            return candidate_ids.tolist()

        except Track.DoesNotExist:
            print(f"Track ID {seed_track_id} not found in database.")
            return []

# Initialize a single instance to be imported by views
recommender_engine = MusicRecommender()