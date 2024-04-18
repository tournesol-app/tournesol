"""
Create and save a public dataset archive on the disk.
"""

import codecs
import zipfile
from os.path import getctime
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.utils import timezone

from core.utils.time import time_ago
from tournesol.lib.public_dataset import (
    write_collective_criteria_scores_file,
    write_comparisons_file,
    write_individual_criteria_scores_file,
    write_metadata_file,
    write_users_file,
    write_vouchers_file,
)
from tournesol.models.poll import Poll


class Command(BaseCommand):
    help = "Create and save a public dataset archive on the disk, then delete old datasets."

    def add_arguments(self, parser):
        parser.add_argument(
            "--keep-only",
            type=int,
            default=10,
            help="The number of archives to keep on the disk (default 10)."
            " The oldest archives will be deleted. No effect when --keep-all is set.",
        )
        parser.add_argument(
            "--keep-all",
            action="store_true",
            default=False,
            help="Do not remove old archives from the disk."
            " Ignore the value defined by --keep-only.",
        )

    def handle(self, *args, **options):
        """
        Create a public dataset archive with fresh data retrieved from the
        database.

        The archive is created on the disk at:
            `MEDIA_ROOT/APP_TOURNESOL["DATASETS_BUILD_DIR"]`
        """
        self.stdout.write(f"start command: {__name__}")

        # Display the configuration if more verbosity is asked.
        if options.get("verbosity", 1) > 1:
            self.stdout.write(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
            self.stdout.write(
                "APP_TOURNESOL['DATASET_BASE_NAME']:"
                f" {settings.APP_TOURNESOL['DATASET_BASE_NAME']}"
            )
            self.stdout.write(
                "APP_TOURNESOL['DATASETS_BUILD_DIR']:"
                f" {settings.APP_TOURNESOL['DATASETS_BUILD_DIR']}"
            )

        dataset_base_name: str = settings.APP_TOURNESOL["DATASET_BASE_NAME"]
        datasets_build_dir = Path(settings.MEDIA_ROOT).joinpath(
            settings.APP_TOURNESOL["DATASETS_BUILD_DIR"]
        )
        datasets_build_dir.mkdir(parents=True, exist_ok=True)
        dataset_base_path = datasets_build_dir / dataset_base_name
        archive_abs_path = dataset_base_path.with_suffix(".zip")
        archive_temp_path = dataset_base_path.with_suffix(".zip.tmp")

        with transaction.atomic():
            cursor = connection.cursor()
            cursor.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
            self.write_archive(archive_temp_path)
            archive_temp_path.rename(archive_abs_path)

        self.stdout.write(self.style.SUCCESS(f"archive created at {archive_abs_path}"))

        # CLEANING phase
        if options["keep_all"]:
            self.stdout.write("the option --keep-all is set, old datasets won't be deleted")
        else:
            all_datasets = list(datasets_build_dir.glob(f"{dataset_base_name}*"))
            all_datasets.sort(key=getctime, reverse=True)

            for old_dataset in all_datasets[options["keep_only"]:]:
                old_dataset.unlink()
                self.stdout.write(f"deleted old {old_dataset}")

        self.stdout.write(self.style.SUCCESS("success"))
        self.stdout.write("end")

    def write_archive(self, archive_abs_path: Path):
        # Only the default poll is exported for the moment.
        poll_name = Poll.default_poll().name

        readme_path = Path("tournesol/resources/export_readme.txt")
        license_path = Path("tournesol/resources/export_odc_by_1.0_public_text.txt")

        first_day_of_week = time_ago(days=timezone.now().weekday()).replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        # BUILDING phase
        with zipfile.ZipFile(archive_abs_path, "w", compression=zipfile.ZIP_DEFLATED) as zip_file:
            with open(readme_path, "r", encoding="utf-8") as readme:
                zip_file.writestr("README.txt", readme.read())

            with open(license_path, "r", encoding="utf-8") as license_file:
                zip_file.writestr("LICENSE.txt", license_file.read())

            with zip_file.open("metadata.json", "w") as output:
                text_output = codecs.getwriter("utf8")(output)
                self.stdout.write("building tournesol metadata...")
                write_metadata_file(text_output, data_until=first_day_of_week)
            self.stdout.write("- metadata.json written.")

            with zip_file.open("users.csv", "w") as output:
                text_output = codecs.getwriter("utf8")(output)
                self.stdout.write("retrieving users' data...")
                write_users_file(poll_name, text_output)
            self.stdout.write("- users.csv written.")

            with zip_file.open("comparisons.csv", "w") as output:
                text_output = codecs.getwriter("utf8")(output)
                self.stdout.write("retrieving comparisons' data...")
                write_comparisons_file(poll_name, text_output, until_=first_day_of_week)
            self.stdout.write("- comparisons.csv written.")

            with zip_file.open("individual_criteria_scores.csv", "w") as output:
                text_output = codecs.getwriter("utf8")(output)
                self.stdout.write("retrieving individual criteria scores' data...")
                write_individual_criteria_scores_file(poll_name, text_output)
            self.stdout.write("- individual_criteria_scores.csv written.")

            with zip_file.open("collective_criteria_scores.csv", "w") as output:
                text_output = codecs.getwriter("utf8")(output)
                self.stdout.write("retrieving collective criteria scores' data...")
                write_collective_criteria_scores_file(poll_name, text_output)
            self.stdout.write("- collective_criteria_scores.csv written.")

            with zip_file.open("vouchers.csv", "w") as output:
                text_output = codecs.getwriter("utf8")(output)
                self.stdout.write("retrieving vouchers data...")
                write_vouchers_file(text_output)
            self.stdout.write("- vouchers.csv written")
