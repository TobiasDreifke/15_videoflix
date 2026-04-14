import mimetypes
import os
from django.http import FileResponse, Http404
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from ..models import Video
from .serializers import VideoSerializer


class VideoListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return all videos available to the authenticated user."""
        videos = Video.objects.all()
        serializer = VideoSerializer(videos, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class VideoDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """Return a single video by primary key."""
        video = get_video_or_none(pk)
        if not video:
            return Response({'error': 'Video nicht gefunden.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = VideoSerializer(video, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        """Delete a single video by primary key."""
        video = get_video_or_none(pk)
        if not video:
            return Response({'error': 'Video nicht gefunden.'}, status=status.HTTP_404_NOT_FOUND)
        video.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ThumbnailDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """Stream the thumbnail image file for a video."""
        video = get_video_or_none(pk)
        if not video or not video.thumbnail:
            raise Http404('Thumbnail nicht gefunden.')

        content_type, _ = mimetypes.guess_type(video.thumbnail.path)
        return FileResponse(
            open(video.thumbnail.path, 'rb'),
            content_type=content_type or 'application/octet-stream',
        )

    def delete(self, request, pk):
        """Delete the thumbnail image assigned to a video."""
        video = get_video_or_none(pk)
        if not video or not video.thumbnail:
            return Response({'error': 'Thumbnail nicht gefunden.'}, status=status.HTTP_404_NOT_FOUND)

        video.thumbnail.delete(save=False)
        video.thumbnail = None
        video.save(update_fields=['thumbnail'])
        return Response(status=status.HTTP_204_NO_CONTENT)


class HLSManifestView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution):
        """Serve the HLS manifest file for a video resolution."""
        manifest_path = build_hls_path(movie_id, resolution, 'index.m3u8')
        if not os.path.exists(manifest_path):
            raise Http404('Manifest nicht gefunden.')
        return FileResponse(open(manifest_path, 'rb'), content_type='application/vnd.apple.mpegurl')


class HLSSegmentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution, segment):
        """Serve a single HLS transport stream segment."""
        segment_path = build_hls_path(movie_id, resolution, segment)
        if not os.path.exists(segment_path):
            raise Http404('Segment nicht gefunden.')
        return FileResponse(open(segment_path, 'rb'), content_type='video/MP2T')


def get_video_or_none(pk):
    """Return a video by primary key or ``None`` if it does not exist."""
    try:
        return Video.objects.get(pk=pk)
    except Video.DoesNotExist:
        return None


def build_hls_path(movie_id, resolution, filename):
    """Build the absolute filesystem path for an HLS asset."""
    return os.path.join(settings.MEDIA_ROOT, 'videos', 'hls', str(movie_id), resolution, filename)
