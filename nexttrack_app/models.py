from django.db import models

class Track(models.Model):
    # Text Data
    track_id = models.CharField(max_length=100, unique=True)
    artists = models.TextField()
    album_name = models.TextField()
    track_name = models.TextField()
    track_genre = models.CharField(max_length=100)
    
    # Numerical Features 
    popularity = models.IntegerField()
    danceability = models.FloatField()
    energy = models.FloatField()
    key = models.IntegerField()
    loudness = models.FloatField()
    mode = models.IntegerField()
    speechiness = models.FloatField()
    acousticness = models.FloatField()
    instrumentalness = models.FloatField()
    liveness = models.FloatField()
    valence = models.FloatField()
    tempo = models.FloatField()

    def __str__(self):
        return f"{self.track_name} - {self.artists}"