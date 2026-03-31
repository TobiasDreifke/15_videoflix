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

def get_video_or_none(pk):
    try:
        return Video.objects.get(pk=pk)
    except Video.DoesNotExist:
        return None