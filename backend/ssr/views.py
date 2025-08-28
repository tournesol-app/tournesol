import typing as tp

import requests
from django.http import HttpResponse, HttpRequest
from django.conf import settings
from django.template.loader import render_to_string

from tournesol.models import Entity
from tournesol.models.entity import TYPE_VIDEO


def get_static_index_html() -> str:
    if settings.DEBUG:
        timeout = 10.0
        try:
            # Try to get index.html from dev-env frontend container
            resp = requests.get("http://tournesol-dev-front:3000", timeout=timeout)
        except requests.ConnectionError:
            resp = requests.get(settings.TOURNESOL_MAIN_URL, timeout=timeout)
        resp.raise_for_status()
        return resp.text
    return (settings.FRONTEND_STATIC_FILES_PATH / "index.html").read_text()


def get_default_meta_tags(request: HttpRequest) -> dict[str, str]:
    full_frontend_path = request.get_full_path().removeprefix("/ssr/")
    return {
        "og:site_name": "Tournesol",
        "og:type": "website",
        "og:title": "Tournesol",
        "og:description": (
            "Compare online content and contribute to the development of "
            "responsible content recommendations."
        ),
        "og:image": f"{settings.MAIN_URL}preview/{full_frontend_path}",
        "og:url": f"{settings.TOURNESOL_MAIN_URL}{full_frontend_path}",
        "twitter:card": "summary_large_image",
    }


def get_entity_meta_tags(uid: str) -> dict[str, str]:
    try:
        entity: Entity = Entity.objects.get(uid=uid)
    except Entity.DoesNotExist:
        return {}

    if entity.type != TYPE_VIDEO:
        return {}

    meta_tags = {
        "og:type": "video",
        "og:video:url": f"https://youtube.com/embed/{entity.video_id}",
        "og:video:type": "text/html",
    }

    if video_title := entity.metadata.get("name"):
        meta_tags["og:title"] = video_title

    if video_channel_name := entity.metadata.get("uploader"):
        meta_tags["og:description"] = video_channel_name

    return meta_tags


def render_tournesol_html_with_dynamic_tags(request: HttpRequest, uid: tp.Optional[str] = None):
    index_html = get_static_index_html()
    meta_tags = get_default_meta_tags(request)
    if uid is not None:
        meta_tags |= get_entity_meta_tags(uid)

    rendered_html = index_html.replace(
        "<!--DJANGO_META_TAGS-->",
        render_to_string(
            "opengraph/meta_tags.html",
            {
                "meta_tags": meta_tags,
            },
        ),
        1,
    )
    return HttpResponse(rendered_html)
