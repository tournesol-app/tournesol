from django.core.management.base import BaseCommand
from backend.add_videos import video_thread_timeout


class Command(BaseCommand):
    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('--config', help="Gin configuration file",
                            type=str, default='backend/add_videos.gin')

    def handle(self, **options):
        video_thread_timeout(options['config'])
