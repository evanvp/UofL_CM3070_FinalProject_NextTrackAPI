import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from nexttrack_app.models import Track 

class Command(BaseCommand):
    help = 'Bulk imports songs from dataset.csv'

    def handle(self, *args, **options):
        # Look for dataset.csv in the root folder (beside manage.py)
        csv_file_path = os.path.join(settings.BASE_DIR, 'dataset.csv')
        
        if not os.path.exists(csv_file_path):
            self.stdout.write(self.style.ERROR(f"CSV not found at: {csv_file_path}"))
            return

        tracks_to_create = []
        seen_ids = set() 

        self.stdout.write("Reading CSV and preparing data...")

        with open(csv_file_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                t_id = row['track_id']
                if t_id not in seen_ids:
                    tracks_to_create.append(Track(
                        track_id=t_id,
                        artists=row['artists'],
                        album_name=row['album_name'],
                        track_name=row['track_name'],
                        popularity=row['popularity'],
                        danceability=row['danceability'],
                        energy=row['energy'],
                        key=row['key'],
                        loudness=row['loudness'],
                        mode=row['mode'],
                        speechiness=row['speechiness'],
                        acousticness=row['acousticness'],
                        instrumentalness=row['instrumentalness'],
                        liveness=row['liveness'],
                        valence=row['valence'],
                        tempo=row['tempo'],
                        track_genre=row['track_genre']
                    ))
                    seen_ids.add(t_id)

        self.stdout.write(f"Importing {len(tracks_to_create)} tracks to Database...")
        
        # Batch upload for speed
        Track.objects.bulk_create(tracks_to_create, batch_size=1000)
        
        self.stdout.write(self.style.SUCCESS('Successfully imported all tracks!'))