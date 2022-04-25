from urllib.parse import quote

import requests
from django.db.models import Q

from tournesol.serializers.metadata import CandidateMetadata

from .base import EntityType

TYPE_CANDIDATE = "candidate_fr_2022"
CANDIDATE_UID_REGEX = r"wd:Q(\d+)"

WIKIDATA_API_BASE_URL = "https://www.wikidata.org/w/api.php"


class CandidateEntity(EntityType):
    name = TYPE_CANDIDATE
    metadata_serializer_class = CandidateMetadata

    @classmethod
    def filter_search(cls, qs, query):
        from tournesol.models import Entity

        return qs.filter(
            pk__in=Entity.objects.filter(Q(metadata__name__icontains=query))
        )

    @classmethod
    def get_uid_regex(cls, namespace: str) -> str:
        return CANDIDATE_UID_REGEX

    @property
    def wikidata_id(self):
        if not self.instance.uid.startswith("wd:"):
            raise AttributeError(f"{self.instance} is not a wikidata entity")
        return self.instance.uid[3:]

    def update_metadata_field(self):
        resp = requests.get(
            WIKIDATA_API_BASE_URL,
            params={
                "action": "wbgetentities",
                "languages": "fr|en",
                "sitefilter": "frwiki",
                "ids": self.wikidata_id,
                "format": "json",
            },
        )
        resp.raise_for_status()
        wd_item = resp.json()["entities"][self.wikidata_id]
        wd_labels = wd_item["labels"]
        wd_claims = wd_item["claims"]

        def get_property_value(property_id):
            return wd_claims[property_id][0]["mainsnak"]["datavalue"]["value"]

        metadata = {
            "name": wd_labels.get("fr", {}).get("value")
            or wd_labels.get("en", {}).get("value"),
            "frwiki_title": wd_item["sitelinks"].get("frwiki", {}).get("title"),
        }

        # Image (P18)
        if "P18" in wd_claims:
            image_file = get_property_value("P18")
            encoded_filename = quote(image_file, safe="")
            image_url = (
                "https://commons.wikimedia.org/wiki"
                + f"/Special:Redirect/file/{encoded_filename}?width=800"
            )
            metadata["image_url"] = image_url

        # Official website (P856)
        if "P856" in wd_claims:
            metadata["website_url"] = get_property_value("P856")

        # Youtube channel ID (P2397)
        if "P2397" in wd_claims:
            metadata["youtube_channel_id"] = get_property_value("P2397")

        # Twitter username (P2002)
        if "P2002" in wd_claims:
            metadata["twitter_username"] = get_property_value("P2002")

        self.instance.metadata = metadata
