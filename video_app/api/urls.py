from django.urls import path
from .views import VideoListView, VideoDetailView, GenreListView, VideoByGenreView

urlpatterns = [
    path('video/', VideoListView.as_view(), name='video-list'),
    path('video/<int:pk>/', VideoDetailView.as_view(), name='video-detail'),
]