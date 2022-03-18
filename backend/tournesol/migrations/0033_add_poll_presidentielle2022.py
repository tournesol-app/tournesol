from urllib.parse import quote

import requests
from django.conf import settings
from django.db import migrations
from django.utils import timezone

CANDIDATES = [
    "wd:Q439490",  # N. Arthaud
    "wd:Q12961",  # N. Dupont-Aignan
    "wd:Q2851133",  # A. Hidalgo
    "wd:Q441791",  # Y. Jadot
    "wd:Q3173022",  # J. Lassalle
    "wd:Q12927",  # M. Le Pen
    "wd:Q3052772",  # E. Macron
    "wd:Q5829",  # JL. Mélenchon
    "wd:Q455023",  # V. Pécresse
    "wd:Q2631198",  # P. Poutou
    "wd:Q30388733",  # F. Roussel
    "wd:Q288477",  # E. Zemmour
]

CRITERIA = [
    {
        "name": "be_president",
        "label_en": "Should be president",
        "label_fr": "Devrait être président.e",
        "optional": False,
    },
    {
        "name": "energy_environment",
        "label_en": "Energy & environment",
        "label_fr": "Énergie & environnement",
        "optional": False,
    },
    {
        "name": "education_culture",
        "label_en": "Education, culture & information",
        "label_fr": "Éducation, culture & information",
        "optional": False,
    },
    {
        "name": "health",
        "label_en": "Health & well-being",
        "label_fr": "Santé & bien-être",
        "optional": False,
    },
    {
        "name": "institutions_democracy",
        "label_en": "Institutions & democracy",
        "label_fr": "Institutions & démocratie",
    },
    {
        "name": "labour_economy",
        "label_en": "Labour & economy",
        "label_fr": "Travail & économie",
    },
    {
        "name": "solidarity",
        "label_en": "Solidarity & inclusivity",
        "label_fr": "Solidarité & inclusion",
    },
    {
        "name": "international",
        "label_en": "International politics",
        "label_fr": "Politique internationale",
    },
]

WIKIDATA_API_BASE_URL = "https://www.wikidata.org/w/api.php"


def refresh_metadata(candidate):
    """
    Fetch and update the candidates' metadata from Wikidata.

    This function needs to be duplicated here, as versioned models used in
    migrations do not include custom methods.
    """
    candidate.last_metadata_request_at = timezone.now()

    resp = requests.get(
        WIKIDATA_API_BASE_URL,
        params={
            "action": "wbgetentities",
            "languages": "fr|en",
            "sitefilter": "frwiki",
            "ids": candidate.uid.split(":")[1],
            "format": "json",
        },
    )
    resp.raise_for_status()
    wd_item = resp.json()["entities"][candidate.uid.split(":")[1]]
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

    candidate.metadata = metadata
    candidate.metadata_timestamp = timezone.now()


def migrate_forward(apps, schema_editor):
    """
    Create the poll `presidentielle2022` with its criteria and its candidates.
    """
    Criteria = apps.get_model("tournesol", "Criteria")
    CriteriaLocale = apps.get_model("tournesol", "CriteriaLocale")
    CriteriaRank = apps.get_model("tournesol", "CriteriaRank")
    Entity = apps.get_model("tournesol", "Entity")
    Poll = apps.get_model("tournesol", "Poll")

    poll = Poll.objects.create(
        name="presidentielle2022", entity_type="candidate_fr_2022"
    )

    for idx, c_data in enumerate(CRITERIA):
        criteria = Criteria.objects.create(name=c_data["name"])
        CriteriaLocale.objects.create(
            criteria=criteria, language="en", label=c_data["label_en"]
        )
        CriteriaLocale.objects.create(
            criteria=criteria, language="fr", label=c_data["label_fr"]
        )
        CriteriaRank.objects.create(
            criteria=criteria,
            poll=poll,
            rank=(len(CRITERIA) - idx) * 10,
            optional=c_data.get("optional", True),
        )

    for uid in CANDIDATES:
        candidate = Entity(type="candidate_fr_2022", uid=uid)
        if settings.ENABLE_API_WIKIDATA["MIGRATIONS"]:
            refresh_metadata(candidate)
        candidate.save()


class Migration(migrations.Migration):

    dependencies = [
        ("tournesol", "0032_alter_entity_type_alter_poll_entity_type"),
    ]

    operations = [
        migrations.RunPython(migrate_forward, migrations.RunPython.noop, atomic=True)
    ]
