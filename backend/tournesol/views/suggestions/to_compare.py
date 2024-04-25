from typing import Optional

from django.db import models
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from tournesol.lib.suggestions.strategies import ClassicEntitySuggestionStrategy
from tournesol.serializers.suggestion import EntityToCompare
from tournesol.utils.http import langs_from_header_accept_language
from tournesol.views import PollScopedViewMixin


class ToCompareStrategy(models.TextChoices):
    CLASSIC = "classic"


@extend_schema_view(
    get=extend_schema(
        parameters=[
            OpenApiParameter(
                name="strategy",
                required=False,
                enum=ToCompareStrategy.values,
                default=ToCompareStrategy.CLASSIC,
                description="The strategy used to suggest a entities to compare.",
            ),
        ],
    )
)
class SuggestionsToCompare(PollScopedViewMixin, generics.ListAPIView):
    """
    Suggest a list of entities to compare to the logged-in user.

    The suggestion strategy is determined by the `strategy` query parameter.
    """

    pagination_class = None
    permission_classes = [IsAuthenticated]
    serializer_class = EntityToCompare

    strategy = None

    # When the user's preferred languages are unknown, use this language.
    fallback_lang = "en"
    # If the user's preferred languages don't contain at least one language
    # from this list, use the fallback language.
    min_lang_set = ["en", "fr"]

    def _get_user_preferred_langs(self, fallback: Optional[str] = None) -> list[str]:
        preferred_langs = self.request.user.get_recommendations_default_langs(
            self.poll_from_url.name
        )

        if preferred_langs is None:
            langs = langs_from_header_accept_language(
                self.request.headers.get("accept-language", "en")
            )
        else:
            langs = preferred_langs

        if fallback and len(langs) > 0:
            if all(lang not in langs for lang in self.min_lang_set):
                langs.append(fallback)

        return langs

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)

        langs = self._get_user_preferred_langs(self.fallback_lang)
        strategy = request.query_params.get("strategy", ToCompareStrategy.CLASSIC)

        if strategy == ToCompareStrategy.CLASSIC:
            self.strategy = ClassicEntitySuggestionStrategy(
                self.poll_from_url, request.user, langs
            )
        else:
            # Fallback to the classic strategy if an unknown strategy is provided.
            self.strategy = ClassicEntitySuggestionStrategy(
                self.poll_from_url, request.user, langs
            )

    def get_queryset(self):
        return self.strategy.get_results()
