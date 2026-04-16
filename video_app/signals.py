import os
import shutil

import django_rq
from django.conf import settings
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from .models import Video


@receiver(pre_save, sender=Video)
def cleanup_replaced_thumbnail(sender, instance, **kwargs):
    """Delete the previous thumbnail file when a video thumbnail is replaced."""
    if not instance.pk:
        return

    try:
        previous = Video.objects.only('thumbnail').get(pk=instance.pk)
    except Video.DoesNotExist:
        return

    if previous.thumbnail and previous.thumbnail.name != getattr(instance.thumbnail, 'name', None):
        previous.thumbnail.delete(save=False)


@receiver(post_save, sender=Video)
def trigger_hls_conversion(sender, instance, created, **kwargs):
    """Queue HLS conversion when a new video file is created."""
    if created and instance.video_file:
        queue = django_rq.get_queue('low')
        queue.enqueue('video_app.utils.convert_to_hls', instance.pk)


@receiver(post_delete, sender=Video)
def cleanup_video_files(sender, instance, **kwargs):
    """Remove stored media files and generated HLS assets after deletion."""
    if instance.video_file:
        instance.video_file.delete(save=False)

    if instance.thumbnail:
        instance.thumbnail.delete(save=False)

    hls_directory = os.path.join(settings.MEDIA_ROOT, 'videos', 'hls', str(instance.pk))
    shutil.rmtree(hls_directory, ignore_errors=True)
