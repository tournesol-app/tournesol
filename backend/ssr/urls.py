from django.urls import path, re_path

from . import views


urlpatterns = [
    path(
        "entities/<str:uid>",
        views.render_tournesol_html_with_dynamic_tags,
        name="ssr_entities",
    ),
    re_path(
        r".*",
        views.render_tournesol_html_with_dynamic_tags,
        name="ssr_default",
    ),
]
