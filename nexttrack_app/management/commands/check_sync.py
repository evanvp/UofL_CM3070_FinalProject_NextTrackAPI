import joblib
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from nexttrack_app.models import Track

class Command(BaseCommand):
    help = 'Checks if the KNN Model indices match the Database IDs'

    def handle(self, *args, **options):
        # Path to ID Map
        mapping_path = os.path.join(settings.BASE_DIR, 'ml_assets', 'model_track_ids.joblib')
        
        if not os.path.exists(mapping_path):
            self.stdout.write(self.style.ERROR(f"Mapping file not found at {mapping_path}"))
            return

        # Load the mapping
        all_ids = joblib.load(mapping_path)
        model_count = len(all_ids)
        db_count = Track.objects.count()

        self.stdout.write(f"Model Track Count: {model_count}")
        self.stdout.write(f"Database Track Count: {db_count}")

        if model_count != db_count:
            self.stdout.write(self.style.WARNING("WARNING: Row counts do not match!"))
        
        # Check the "Bookends" (First and Last)
        first_db = Track.objects.all().order_by('id').first()
        last_db = Track.objects.all().order_by('id').last()

        # Check First
        if first_db.track_id == all_ids[0]:
            self.stdout.write(self.style.SUCCESS(f"First track matches: {first_db.track_name}"))
        else:
            self.stdout.write(self.style.ERROR(f"First track mismatch! Model expects {all_ids[0]}, DB has {first_db.track_id}"))

        # Check Last
        if last_db.track_id == all_ids[-1]:
            self.stdout.write(self.style.SUCCESS(f"Last track matches: {last_db.track_name}"))
        else:
            self.stdout.write(self.style.ERROR(f"Last track mismatch! Model expects {all_ids[-1]}, DB has {last_db.track_id}"))