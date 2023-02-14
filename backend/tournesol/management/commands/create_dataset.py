"""
Create and save a public dataset archive on the disk.
"""
import os
import zipfile
from io import StringIO

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from tournesol.lib.public_dataset import (
    write_comparisons_file,
    write_individual_criteria_scores_file,
    write_users_file,
)
from tournesol.models.poll import Poll


class Command(BaseCommand):
    help = "Create and save a public dataset archive on the disk."

    def handle(self, *args, **options):
        """
        Create a public dataset archive with fresh data retrieved from the
        database.

        The archive is created on the disk at:
            `MEDIA_ROOT/APP_TOURNESOL["DATASET_BUILD_DIR"]`
        """
        self.stdout.write(f"start command: {__name__}")

        dataset_dir = os.path.join(
            settings.MEDIA_ROOT, settings.APP_TOURNESOL["DATASET_BUILD_DIR"]
        )

        try:
            os.makedirs(dataset_dir)
        except FileExistsError:
            pass

        # Only the default poll is exported for the moment.
        poll_name = Poll.default_poll().name

        archive_name = f"tournesol_dataset_{timezone.now().strftime('%Y%m%dT%H%M%SZ')}"
        archive_root = os.path.join(dataset_dir, archive_name)
        readme_path = "tournesol/resources/export_readme.txt"

        with zipfile.ZipFile(archive_root, "w", compression=zipfile.ZIP_DEFLATED) as zip_file:
            with open(readme_path, "r", encoding="utf-8") as readme_file:
                zip_file.writestr(f"{archive_name}/README.txt", readme_file.read())

            with StringIO() as output:
                self.stdout.write("retrieving users' data...")
                write_users_file(poll_name, output)
                zip_file.writestr(f"{archive_name}/users.csv", output.getvalue())
                self.stdout.write("- users.csv written.")

            with StringIO() as output:
                self.stdout.write("retrieving comparisons' data...")
                write_comparisons_file(poll_name, output)
                zip_file.writestr(f"{archive_name}/comparisons.csv", output.getvalue())
                self.stdout.write("- comparisons.csv written.")

            with StringIO() as output:
                self.stdout.write("retrieving individual criteria scores' data...")
                write_individual_criteria_scores_file(poll_name, output)
                zip_file.writestr(
                    f"{archive_name}/individual_criteria_scores.csv", output.getvalue()
                )
                self.stdout.write("- individual_criteria_scores.csv written.")

        self.stdout.write(self.style.SUCCESS(f"archive created at {archive_root}"))
        self.stdout.write(self.style.SUCCESS("success"))
        self.stdout.write("end")
