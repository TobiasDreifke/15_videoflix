from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Video
import django_rq


@receiver(post_save, sender=Video)
def trigger_hls_conversion(sender, instance, created, **kwargs):
    if created and instance.video_file:
        queue = django_rq.get_queue('default')
        queue.enqueue('video_app.utils.convert_to_hls', instance.pk)