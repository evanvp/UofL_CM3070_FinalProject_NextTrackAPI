import random
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Track
from .serializers import TrackSerializer
from .recommender_service import recommender_engine
import requests
from django.conf import settings
from django.http import JsonResponse


# Handle the very first song seleciton
class InitialTrackAPIView(APIView):
    def get(self, request):
        # Check if a specific track was requested via ID
        target_id = request.query_params.get('track_id')
        
        if target_id:
            try:
                # Prioritize looking up the specific track
                track = Track.objects.get(track_id=target_id)
                serializer = TrackSerializer(track)
                return Response(serializer.data)
            except Track.DoesNotExist:
                # If ID is invalid, shows either error or fall back to random
                return Response({"error": "Specific track not found"}, status=404)

        # Fallback to the original Random/Genre logic
        genre = request.query_params.get('genre')
        
        if genre:
            queryset = Track.objects.filter(track_genre__iexact=genre)
        else:
            queryset = Track.objects.all()

        count = queryset.count()
        if count == 0:
            return Response({"error": "No tracks found"}, status=404)
        
        random_index = random.randint(0, count - 1)
        random_track = queryset[random_index]

        serializer = TrackSerializer(random_track)
        return Response(serializer.data)

# Handle the subsequent music recommendation 
class RecommendationAPIView(APIView):
    def get(self, request):
        seed_id = request.query_params.get('track_id')
        vibe = request.query_params.get('vibe')
        genre = request.query_params.get('genre')

        if not seed_id:
            return Response({"error": "Missing seed track_id"}, status=400)

        try:
            # Get the current song to establish "Identity"
            current_song = Track.objects.get(track_id=seed_id)
            
            # Get 150 neighbors 
            candidate_ids = recommender_engine.get_candidate_pool(seed_id)
            
            # Fetch all potential tracks from DB
            tracks_pool = Track.objects.filter(track_id__in=candidate_ids)
            
            # this is for leveraing search O(1) unsorted result from database and sorted result from model
            track_map = {t.track_id: t for t in tracks_pool}

            final_list = []
            is_fallback = False
            seen_identities = set()
            
            # Add current song to "seen" to prevent duplicates 
            current_identity = (current_song.track_name.lower().strip(), current_song.artists.lower().strip())
            seen_identities.add(current_identity)

            # Filter and Clean
            for tid in candidate_ids:
                track = track_map.get(tid)
                if not track: continue

                # Check Duplicate (Name + Artist)
                identity = (track.track_name.lower().strip(), track.artists.lower().strip())
                if identity in seen_identities:
                    continue

                # Apply Vibe/Genre filters 
                if not self.passes_logic(track, vibe, genre):
                    continue

                final_list.append(track)
                seen_identities.add(identity)

                if len(final_list) >= 10: break

            if not final_list:
                is_fallback = True
                for tid in candidate_ids:
                    track = track_map.get(tid)
                    if not track: continue

                    if track.track_id != seed_id:
                        final_list.append(track)
                    
                    if len(final_list) >= 10: break

            serializer = TrackSerializer(final_list, many=True)
            return Response({
            "tracks": serializer.data,
            "is_fallback": is_fallback,
            "message": "Showing similar tracks (Vibe filter yielded no results)" if is_fallback else "Matches found!"
        })

        except Track.DoesNotExist:
            return Response({"error": "Seed track not found"}, status=404)

    def passes_logic(self, track, vibe, genre):
        # Only check genre if user requested it
        if genre and (track.track_genre is None or track.track_genre.lower() != genre.lower()):
            return False

        # Only check vibe fields if user requested a vibe
        if vibe == 'focus':
            if track.danceability is None or track.speechiness is None: return False
            return track.danceability < 0.5 or track.speechiness < 0.05
        
        elif vibe == 'party':
            if track.energy is None or track.danceability is None: return False
            return track.energy > 0.5 or track.danceability > 0.5
            
        elif vibe == 'chill':
            if track.energy is None or track.valence is None: return False
            return track.energy < 0.6 or track.valence > 0.2
            
        elif vibe == 'workout':
            if track.tempo is None or track.energy is None: return False
            return track.tempo > 110 or track.energy > 0.6
        
        return True # Default: Every track passes if no vibe/genre is set
    
def youtube_search(request):
    query = request.GET.get('q')
    api_key = "AIzaSyBJWipCcupBmWHQhSgVqfn5PaCifBMQqQA"  
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&type=video&maxResults=1&key={api_key}"
    
    response = requests.get(url).json()
    
    try:
        video_id = response['items'][0]['id']['videoId']
        return JsonResponse({'video_id': video_id})
    except (KeyError, IndexError):
        return JsonResponse({'video_id': None})