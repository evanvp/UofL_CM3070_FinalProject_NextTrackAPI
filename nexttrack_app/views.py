from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

from .models import Track

def index_page(request):
    # Fetch all unique genres from the database column 'track_genre'
    # .distinct() ensures no duplicated items
    # .order_by() keeps them alphabetical
    genres_list = Track.objects.values_list('track_genre', flat=True).distinct().order_by('track_genre')
    
    # Clean the list by removing None or empty values
    genres = [g for g in genres_list if g]

    return render(request, 'nexttrack_app/index.html', {'genres': genres})


def player_page(request):
    # Pass the genres here too so the "re-select genre" dropdown has options
    genres_query = Track.objects.values_list('track_genre', flat=True).distinct().order_by('track_genre')
    genres = [g for g in genres_query if g]
    return render(request, 'nexttrack_app/player.html', {'genres': genres})
