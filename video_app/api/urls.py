from django.urls import path
from .views import (
    VideoListView,
    VideoDetailView,
    ThumbnailDetailView,
    HLSManifestView,
    HLSSegmentView,
)

urlpatterns = [
    path('video/', VideoListView.as_view(), name='video-list'),
    path('video/<int:pk>/', VideoDetailView.as_view(), name='video-detail'),
    path('video/<int:pk>/thumbnail/', ThumbnailDetailView.as_view(), name='video-thumbnail-detail'),
    path('video/<int:movie_id>/<str:resolution>/index.m3u8', HLSManifestView.as_view(), name='hls-manifest'),
    path('video/<int:movie_id>/<str:resolution>/<str:segment>/', HLSSegmentView.as_view(), name='hls-segment'),
]
