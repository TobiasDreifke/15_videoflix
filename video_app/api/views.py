import os
from django.http import FileResponse, Http404
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from ..models import Video, Genre
from .serializers import VideoSerializer, GenreSerializer


class VideoListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        videos = Video.objects.all()
        serializer = VideoSerializer(videos, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class VideoDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        video = get_video_or_none(pk)
        if not video:
            return Response({'error': 'Video nicht gefunden.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = VideoSerializer(video, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        video = get_video_or_none(pk)
        if not video:
            return Response({'error': 'Video nicht gefunden.'}, status=status.HTTP_404_NOT_FOUND)
        video.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class HLSManifestView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution):
        manifest_path = build_hls_path(movie_id, resolution, 'index.m3u8')
        if not os.path.exists(manifest_path):
            raise Http404('Manifest nicht gefunden.')
        return FileResponse(open(manifest_path, 'rb'), content_type='application/vnd.apple.mpegurl')


class HLSSegmentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution, segment):
        segment_path = build_hls_path(movie_id, resolution, segment)
        if not os.path.exists(segment_path):
            raise Http404('Segment nicht gefunden.')
        return FileResponse(open(segment_path, 'rb'), content_type='video/MP2T')


def get_video_or_none(pk):
    try:
        return Video.objects.get(pk=pk)
    except Video.DoesNotExist:
        return None


def build_hls_path(movie_id, resolution, filename):
    return os.path.join(settings.MEDIA_ROOT, 'videos', 'hls', str(movie_id), resolution, filename)
