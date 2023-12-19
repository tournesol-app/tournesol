"""
Administration interface of the `tournesol` app.
"""

from datetime import datetime

from django.contrib import admin, messages
from django.contrib.admin.filters import SimpleListFilter
from django.db.models import Q, QuerySet
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from sql_util.utils import SubqueryCount

from tournesol.models.entity_context import EntityContext, EntityContextLocale

from .entities.video import YOUTUBE_PUBLISHED_AT_FORMAT
from .models import (
    Comparison,
    ComparisonCriteriaScore,
    ContributorRating,
    ContributorRatingCriteriaScore,
    ContributorScaling,
    Criteria,
    CriteriaLocale,
    CriteriaRank,
    Entity,
    EntityCriteriaScore,
    EntityPollRating,
    Poll,
)
from .utils.video_language import LANGUAGE_CODE_TO_NAME_MATCHING


class MetadataFieldFilter(SimpleListFilter):
    """Used for metadata filters on entities"""

    parameter_name = None
    metadata_key = None

    def lookups(self, request, model_admin):
        """List the possible metadata filters on entities"""
        field_values = sorted(
            model_admin.model.objects.distinct()
            .exclude(**{f"entity__metadata__{self.metadata_key}": None})
            .values_list(f"entity__metadata__{self.metadata_key}", flat=True)
        )
        return [("", "-")] + [(v, v) for v in field_values]

    def queryset(self, request, queryset):
        """Filter the queryset according to the selected metadata filter"""
        if self.value():
            json_field_query = {f"entity__metadata__{self.metadata_key}": self.value()}
            return queryset.filter(**json_field_query)
        if self.value() == "":
            json_field_query = Q(**{f"entity__metadata__{self.metadata_key}": ""}) | Q(
                **{f"entity__metadata__{self.metadata_key}": None}
            )
            return queryset.filter(json_field_query)
        return queryset


class EntityLanguageFilter(MetadataFieldFilter):
    """Enables the language filter in the entities' admin interface"""

    title = "language"
    parameter_name = "metadataLanguage"
    metadata_key = "language"


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    list_display = (
        "uid",
        "get_name",
        "link_to_tournesol",
    )
    search_fields = ("uid", "metadata__name")
    list_filter = ("type",)
    actions = ["update_metadata"]

    @admin.action(description="Force metadata refresh of selected entities")
    def update_metadata(self, request, queryset: QuerySet[Entity]):
        count = 0
        for entity in queryset.iterator():
            entity.inner.refresh_metadata(force=True)
            count += 1
        messages.info(
            request,
            _("Successfully refreshed the metadata of %(count)s entities.") % {"count": count},
        )

    @staticmethod
    @admin.display(description="name", ordering="metadata__name")
    def get_name(obj):
        return obj.metadata.get("name")

    @staticmethod
    @admin.display(description="uploader", ordering="metadata__uploader")
    def get_uploader(obj):
        return obj.metadata.get("uploader")

    @staticmethod
    @admin.display(description="publication_date", ordering="metadata__publication_date")
    def get_publication_date(obj):
        return obj.metadata.get("publication_date")


@admin.register(EntityPollRating)
class EntityPollRatingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "entity_link",
        "poll",
        "get_name",
        "get_uploader",
        "get_publication_date",
        "get_tournesol_score",
        "n_comparisons",
        "n_contributors",
        "sum_trust_scores",
        "get_language",
        "get_link_to_tournesol",
    )
    list_filter = (
        "poll",
        EntityLanguageFilter,
    )
    search_fields = ("entity__uid", "entity__metadata__name", "entity__metadata__uploader")
    list_select_related = ("poll", "entity")
    raw_id_fields = ("entity",)
    readonly_fields = ("poll", "entity", "tournesol_score", "n_comparisons", "n_contributors")

    def entity_link(self, obj):
        entity = obj.entity
        app_label = entity._meta.app_label
        model_label = entity._meta.model_name
        url = reverse(f"admin:{app_label}_{model_label}_change", args=(entity.id,))
        return format_html(f'<a href="{url}">{entity.uid}</a>')

    @staticmethod
    @admin.display(description="name", ordering="entity__metadata__name")
    def get_name(obj):
        return obj.entity.metadata.get("name")

    @staticmethod
    @admin.display(description="uploader", ordering="entity__metadata__uploader")
    def get_uploader(obj):
        return obj.entity.metadata.get("uploader")

    @staticmethod
    @admin.display(description="publication date", ordering="entity__metadata__publication_date")
    def get_publication_date(obj):
        pub_date = obj.entity.metadata.get("publication_date")

        if pub_date:
            try:
                return datetime.strptime(pub_date, YOUTUBE_PUBLISHED_AT_FORMAT)
            except ValueError:
                # Fallback to the legacy format.
                return datetime.strptime(pub_date, "%Y-%m-%d")
        return pub_date

    @staticmethod
    @admin.display(description="Tournesol score", ordering="tournesol_score")
    def get_tournesol_score(obj):
        try:
            return round(obj.tournesol_score, 2)
        except TypeError:
            return obj.tournesol_score

    @staticmethod
    @admin.display(description="language", ordering="entity__metadata__language")
    def get_language(obj):
        language_code = obj.entity.metadata.get("language")
        return LANGUAGE_CODE_TO_NAME_MATCHING.get(language_code, language_code)

    @staticmethod
    @admin.display(description="link")
    def get_link_to_tournesol(obj):
        return obj.entity.link_to_tournesol()


@admin.register(EntityCriteriaScore)
class EntityCriteriaScoreAdmin(admin.ModelAdmin):
    list_display = ("entity", "poll", "criteria", "score_mode", "score")
    list_filter = (
        "poll",
        "score_mode",
    )
    search_fields = ("entity__uid",)
    raw_id_fields = ("entity",)


@admin.register(ContributorRating)
class ContributorRatingAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "entity",
        "get_poll_name",
        "link_to_tournesol",
        "is_public",
    )
    list_filter = (
        "poll__name",
        "entity__type",
        "is_public",
    )
    list_select_related = (
        "poll",
        "entity",
    )

    def link_to_tournesol(self, obj):
        return obj.entity.link_to_tournesol()

    @admin.display(ordering="poll__name", description="Poll")
    def get_poll_name(self, obj):
        return obj.poll.name


@admin.register(ContributorRatingCriteriaScore)
class ContributorRatingCriteriaScoreAdmin(admin.ModelAdmin):
    list_filter = ("contributor_rating__poll__name",)
    list_display = (
        "id",
        "contributor_rating",
        "criteria",
        "score",
        "voting_right",
    )
    readonly_fields = ("contributor_rating",)
    search_fields = ("contributor_rating__entity__uid",)


@admin.register(ContributorScaling)
class ContributorScalingAdmin(admin.ModelAdmin):
    search_fields = (
        "criteria",
        "user__username",
    )
    list_filter = ("poll__name",)
    list_display = ("id", "user", "criteria", "translation", "scale")
    readonly_fields = ("user",)


@admin.register(Comparison)
class ComparisonAdmin(admin.ModelAdmin):
    search_fields = (
        "user__username",
        "entity_1__uid",
        "entity_2__uid",
    )
    list_display = (
        "pk",
        "user",
        "get_poll_name",
        "entity_1_link",
        "entity_2_link",
        "datetime_lastedit",
    )
    list_filter = ("poll__name",)
    list_select_related = (
        "entity_1",
        "entity_2",
        "poll",
    )
    raw_id_fields = (
        "user",
        "entity_1",
        "entity_2",
    )

    def entity_1_link(self, obj):
        entity = obj.entity_1
        app_label = entity._meta.app_label
        model_label = entity._meta.model_name
        url = reverse(f"admin:{app_label}_{model_label}_change", args=(entity.id,))
        return format_html(f'<a href="{url}">{entity.uid}</a>')

    def entity_2_link(self, obj):
        entity = obj.entity_2
        app_label = entity._meta.app_label
        model_label = entity._meta.model_name
        url = reverse(f"admin:{app_label}_{model_label}_change", args=(entity.id,))
        return format_html(f'<a href="{url}">{entity.uid}</a>')

    @admin.display(ordering="poll__name", description="Poll")
    def get_poll_name(self, obj):
        return obj.poll.name


@admin.register(ComparisonCriteriaScore)
class ComparisonCriteriaScoreAdmin(admin.ModelAdmin):
    list_filter = ("comparison__poll__name",)
    list_display = ("id", "comparison", "criteria", "score")
    readonly_fields = ("comparison",)
    search_fields = (
        "criteria",
        "comparison__entity_1__uid",
        "comparison__entity_2__uid",
    )


class CriteriasInline(admin.TabularInline):
    """Used to display the criteria in the polls' admin interface"""

    model = CriteriaRank
    extra = 0


class CriteriaLocalesInline(admin.TabularInline):
    """Used to display the localization in the criteria's admin interface"""

    model = CriteriaLocale
    extra = 0


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "active",
        "algorithm",
        "entity_type",
        "get_n_criteria",
        "get_n_comparisons",
        "get_n_comparisons_per_criteria",
        "get_proof_of_vote_file",
    )
    list_filter = ("active", "algorithm", "entity_type")
    inlines = (CriteriasInline,)

    def get_queryset(self, request):
        qst = super().get_queryset(request)
        qst = qst.annotate(n_criteria=SubqueryCount("criterias"))
        qst = qst.annotate(n_comparisons=SubqueryCount("comparisons"))
        qst = qst.annotate(
            n_comparisons_per_criteria=SubqueryCount("comparisons__criteria_scores")
        )
        return qst

    @admin.display(description="# criterias", ordering="-n_criteria")
    def get_n_criteria(self, obj):
        return obj.n_criteria

    @admin.display(description="# comparisons", ordering="-n_comparisons")
    def get_n_comparisons(self, obj):
        return obj.n_comparisons

    @admin.display(
        description="# comparisons (x criteria)",
        ordering="-n_comparisons_per_criteria",
    )
    def get_n_comparisons_per_criteria(self, obj):
        return obj.n_comparisons_per_criteria

    @admin.display(description="Proof of vote")
    def get_proof_of_vote_file(self, obj):
        return format_html(
            "<a href={url}>CSV</a>",
            url=reverse("tournesol:export_poll_proof_of_vote", kwargs={"poll_name": obj.name}),
        )


@admin.register(Criteria)
class CriteriaAdmin(admin.ModelAdmin):
    inlines = (CriteriaLocalesInline,)


class HasTextListFilter(admin.SimpleListFilter):
    title = _("has text?")
    parameter_name = "has_text"

    def lookups(self, request, model_admin):
        return (
            (1, _("Yes")),
            (0, _("No")),
        )

    def queryset(self, request, queryset):
        if self.value() == "1":
            return queryset.filter(
                texts__isnull=False,
            )
        if self.value() == "0":
            return queryset.filter(
                texts__isnull=True,
            )
        return queryset


class EntityContextLocaleInline(admin.StackedInline):
    model = EntityContextLocale
    extra = 0


@admin.register(EntityContext)
class EntityContextAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("name", "poll", "origin", "created_at", "has_text", "unsafe", "enabled")
    list_filter = ("poll", "origin", HasTextListFilter, "unsafe", "enabled")
    ordering = ("-created_at",)
    inlines = (EntityContextLocaleInline,)

    def get_queryset(self, request):
        qst = super().get_queryset(request)
        qst = qst.prefetch_related("texts").select_related("poll")
        return qst

    @admin.display(description="has text?", boolean=True)
    def has_text(self, obj) -> bool:
        return obj.texts.exists()
