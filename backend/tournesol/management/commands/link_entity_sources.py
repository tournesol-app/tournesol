import time
from collections import defaultdict

from django.core.management.base import BaseCommand, CommandError

from tournesol.models import Entity, EntitySource, EntitySourceLink

SECONDS_PER_DAY = 24 * 60 * 60
DEFAULT_API_CALLS_PER_DAY = 1000


class Command(BaseCommand):
    help = (
        "Link the entities that have no source yet to the sources named in their metadata,"
        " and stop when they are all done. Unknown sources are created with their metadata,"
        " fetched from their platform in grouped API calls, paced to stay within a daily"
        " budget. The command can be interrupted and run again: it continues where it stopped."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--api-calls-per-day",
            type=int,
            default=DEFAULT_API_CALLS_PER_DAY,
            help="The pace of the API calls fetching unknown sources"
            f" (default: {DEFAULT_API_CALLS_PER_DAY}).",
        )

    def handle(self, *args, api_calls_per_day=DEFAULT_API_CALLS_PER_DAY, **options):
        if api_calls_per_day <= 0:
            raise CommandError("--api-calls-per-day must be positive")
        seconds_between_api_calls = SECONDS_PER_DAY / api_calls_per_day

        self.stdout.write(f"start command: {__name__}")
        entity_ids_by_source_uid = self.get_entity_ids_without_source_by_source_uid()
        known_source_uids = set(
            EntitySource.objects.filter(uid__in=entity_ids_by_source_uid.keys()).values_list(
                "uid", flat=True
            )
        )
        unknown_source_uids = sorted(entity_ids_by_source_uid.keys() - known_source_uids)
        batch_size = EntitySource.MAX_SOURCES_PER_REQUEST
        batches = [
            unknown_source_uids[batch_start:batch_start + batch_size]
            for batch_start in range(0, len(unknown_source_uids), batch_size)
        ]

        link_count = self.link_entities(entity_ids_by_source_uid, known_source_uids)
        self.stdout.write(
            f"Created {link_count} links to {len(known_source_uids)} known sources."
            f" {len(unknown_source_uids)} unknown sources to fetch in {len(batches)} API calls,"
            f" one every {seconds_between_api_calls:.0f} seconds.",
        )

        not_found_source_count = 0
        for batch_number, batch_source_uids in enumerate(batches, start=1):
            if batch_number > 1:
                time.sleep(seconds_between_api_calls)

            try:
                found_source_count = EntitySource.create_from_uids(batch_source_uids)
            except Exception as error:
                raise CommandError(
                    f"API call {batch_number} failed, run the command again to continue: {error}"
                ) from error
            not_found_source_count += len(batch_source_uids) - found_source_count

            link_count = self.link_entities(entity_ids_by_source_uid, batch_source_uids)
            self.stdout.write(
                f"API call {batch_number}/{len(batches)}:"
                f" created {found_source_count} sources and {link_count} links."
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. {not_found_source_count} sources were not found on their platform."
            )
        )
        self.stdout.write("end")

    @staticmethod
    def get_entity_ids_without_source_by_source_uid() -> dict[str, list[int]]:
        entity_ids_by_source_uid = defaultdict(list)
        entities_without_source = (
            Entity.objects.filter(source_links__isnull=True)
            .only("id", "type", "metadata")
            .iterator()
        )
        for entity in entities_without_source:
            for source_uid in entity.inner.get_source_uids():
                entity_ids_by_source_uid[source_uid].append(entity.id)
        return entity_ids_by_source_uid

    @staticmethod
    def link_entities(entity_ids_by_source_uid, source_uids) -> int:
        """Link the entities to those of `source_uids` that exist, and return the link count."""
        existing_source_uids_and_ids = EntitySource.objects.filter(
            uid__in=source_uids
        ).values_list("uid", "id")
        links = [
            EntitySourceLink(entity_id=entity_id, entity_source_id=source_id)
            for source_uid, source_id in existing_source_uids_and_ids
            for entity_id in entity_ids_by_source_uid[source_uid]
        ]
        EntitySourceLink.objects.bulk_create(links, ignore_conflicts=True, batch_size=1000)
        return len(links)
