from django.db import models





class Video(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, related_name='videos')
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    video_file = models.FileField(upload_to='videos/raw/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title