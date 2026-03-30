from rest_framework import serializers
from ..models import Video, Genre


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name']


class VideoSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(read_only=True)
    hls_url = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = ['id', 'title', 'description', 'genre', 'thumbnail', 'hls_url', 'created_at']

    def get_hls_url(self, obj):
        request = self.context.get('request')
        hls_path = f'/media/videos/hls/{obj.pk}/720p/index.m3u8'
        if request:
            return request.build_absolute_uri(hls_path)
        return hls_path