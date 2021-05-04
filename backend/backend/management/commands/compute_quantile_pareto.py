from django.core.management.base import BaseCommand
from backend.models import Video


class Command(BaseCommand):
    def handle(self, **options):
        print("Computing quantiles...")
        Video.recompute_quantiles()

        print("Computing pareto optimality...")
        Video.recompute_pareto()
