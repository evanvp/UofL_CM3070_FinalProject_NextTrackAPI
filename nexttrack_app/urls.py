from django.urls import path
from . import views
from . import api

urlpatterns = [
    path('', views.index_page, name='home'),
    path('player/', views.player_page, name='player_page'),


    path('api/recommendations/', api.RecommendationAPIView.as_view(), name='api_recommendations'),
    path('api/initial-track/', api.InitialTrackAPIView.as_view(), name='api_initial_track'), 
    path('api/youtube-search/', api.youtube_search, name='youtube_search'),
]
