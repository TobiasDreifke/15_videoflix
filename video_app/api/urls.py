from django.urls import path
from .views import VideoListView, VideoDetailView, GenreListView, VideoByGenreView

urlpatterns = [
    path('videos/', VideoListView.as_view(), name='video-list'),
    path('videos/<int:pk>/', VideoDetailView.as_view(), name='video-detail'),
    path('genres/', GenreListView.as_view(), name='genre-list'),
    path('genres/<int:genre_id>/videos/', VideoByGenreView.as_view(), name='videos-by-genre'),
]