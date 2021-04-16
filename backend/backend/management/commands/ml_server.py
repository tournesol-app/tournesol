from django.core.management.base import BaseCommand
from backend.ml_models import run_server


class Command(BaseCommand):
    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('--port', help='Port to listen at', type=int,
                            default=5000)

    def handle(self, **options):
        run_server(port=options['port'])
