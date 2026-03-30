from django.contrib import admin
from .models import Video, Genre

admin.site.register(Genre)


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'genre', 'created_at']