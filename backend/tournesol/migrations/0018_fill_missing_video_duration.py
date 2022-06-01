import logging
from django.db import migrations
from django.utils import timezone
from django.utils.dateparse import parse_duration
from tournesol.utils.api_youtube import get_video_metadata, VideoNotFound


def refresh_youtube_metadata(video):
    """
    Fetch and update video metadata from Youtube API.

    This function is similar to `video.refresh_youtube_metatada(force=True)`
    but this code needs to be duplicated here, as versioned model used
    in migrations do not include model custom methods.
    """
    video.last_metadata_request_at = timezone.now()
    video.save(update_fields=["last_metadata_request_at"])
    try:
        metadata = get_video_metadata(video.video_id, compute_language=False)
    except VideoNotFound:
        metadata = {}

    if not metadata:
        return

    fields = [
        "name",
        "description",
        "publication_date",
        "uploader",
        "views",
    ]
    for f in fields:
        setattr(video, f, metadata[f])

    video.duration = parse_duration(str(metadata["duration"]))
    video.metadata_timestamp = timezone.now()
    logging.info(
        "Saving metadata for video %s. Duration: %s", video.video_id, video.duration
    )
    video.save(update_fields=fields)


def forward_func(apps, schema_editor):
    """
    Refresh video metadata where duration is missing, due to previous implementation
    """
    Video = apps.get_model("tournesol", "Video")
    for video in Video.objects.filter(duration__isnull=True).iterator():
        refresh_youtube_metadata(video)


class Migration(migrations.Migration):

    dependencies = [
        ("tournesol", "0017_video_views_as_bigint"),
    ]

    operations = [
        migrations.RunPython(code=forward_func, reverse_code=migrations.RunPython.noop)
    ]
