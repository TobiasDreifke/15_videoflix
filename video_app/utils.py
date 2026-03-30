import subprocess
import os
from django.conf import settings


def convert_to_hls(video_id):
    from .models import Video
    video = Video.objects.get(pk=video_id)
    input_path = os.path.join(settings.MEDIA_ROOT, str(video.video_file))
    output_base = os.path.join(settings.MEDIA_ROOT, 'videos', 'hls', str(video_id))
    os.makedirs(output_base, exist_ok=True)
    resolutions = [
        ('480p', '854x480', '1400k'),
        ('720p', '1280x720', '2800k'),
        ('1080p', '1920x1080', '5000k'),
    ]
    for name, size, bitrate in resolutions:
        convert_resolution(input_path, output_base, name, size, bitrate)


def convert_resolution(input_path, output_base, name, size, bitrate):
    output_dir = os.path.join(output_base, name)
    os.makedirs(output_dir, exist_ok=True)
    output_m3u8 = os.path.join(output_dir, 'index.m3u8')
    subprocess.run([
        'ffmpeg', '-i', input_path,
        '-vf', f'scale={size}',
        '-b:v', bitrate,
        '-hls_time', '10',
        '-hls_playlist_type', 'vod',
        '-hls_segment_filename', os.path.join(output_dir, 'segment_%03d.ts'),
        output_m3u8,
        '-y'
    ], check=True)