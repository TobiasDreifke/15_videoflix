from rest_framework import serializers
from ..models import Video, Genre


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name']


class VideoSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = ['id', 'created_at', 'title', 'description', 'thumbnail', 'thumbnail_url', 'category']

    def get_category(self, obj):
        return obj.genre.name if obj.genre else None

    def get_thumbnail(self, obj):
        return self._build_thumbnail_url(obj)

    def get_thumbnail_url(self, obj):
        return self._build_thumbnail_url(obj)

    def _build_thumbnail_url(self, obj):
        request = self.context.get('request')
        if obj.thumbnail and request:
            return request.build_absolute_uri(f'/api/video/{obj.pk}/thumbnail/')
        return None
