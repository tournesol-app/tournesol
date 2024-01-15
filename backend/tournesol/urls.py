"""
The `tournesol` app routes.
"""

from django.urls import include, path, re_path
from rest_framework import routers

from .views import ComparisonDetailApi, ComparisonListApi, ComparisonListFilteredApi
from .views.contributor_recommendations import (
    PrivateContributorRecommendationsView,
    PublicContributorRecommendationsView,
)
from .views.criteria_correlations import ContributorCriteriaCorrelationsView
from .views.email_domains import EmailDomainsList
from .views.entities import EntitiesViewSet
from .views.entities_to_compare import EntitiesToCompareView
from .views.exports import (
    ExportAllView,
    ExportComparisonsView,
    ExportProofOfVoteView,
    ExportPublicAllView,
    ExportPublicComparisonsView,
)
from .views.inconsistencies import Length3Cycles, ScoreInconsistencies
from .views.polls import (
    PollsCriteriaScoreDistributionView,
    PollsEntityView,
    PollsRecommendationsView,
    PollsView,
)
from .views.polls_reco_random import RandomRecommendationList
from .views.previews import (
    DynamicWebsitePreviewComparison,
    DynamicWebsitePreviewDefault,
    DynamicWebsitePreviewEntity,
    DynamicWebsitePreviewFAQ,
    DynamicWebsitePreviewRecommendations,
)
from .views.previews.recommendations import get_preview_recommendations_redirect_params
from .views.proof import ProofView
from .views.rate_later import RateLaterDetail, RateLaterList
from .views.ratings import (
    ContributorRatingDetail,
    ContributorRatingList,
    ContributorRatingUpdateAll,
)
from .views.stats import StatisticsView
from .views.subsamples import SubSamplesList
from .views.suggestions.to_compare import SuggestionsToCompare
from .views.unconnected_entities import UnconnectedEntitiesView
from .views.user import CurrentUserView
from .views.video import VideoViewSet

router = routers.DefaultRouter()
router.register(r"video", VideoViewSet, basename="video")
router.register(r"entities", EntitiesViewSet)

app_name = "tournesol"
urlpatterns = [
    path("", include(router.urls)),
    # User API
    path("users/me/", CurrentUserView.as_view(), name="users_me"),
    # User settings API
    path("users/me/", include("core.urls.user_settings")),
    # Voucher API
    path("users/me/", include("vouch.urls")),
    # Data exports
    path(
        "users/me/exports/comparisons/",
        ExportComparisonsView.as_view(),
        name="export_comparisons",
    ),
    path("users/me/exports/all/", ExportAllView.as_view(), name="export_all"),
    path(
        "users/me/entities_to_compare/<str:poll_name>/",
        EntitiesToCompareView.as_view(),
        name="get_entities_to_compare",
    ),
    path(
        "exports/comparisons/",
        ExportPublicComparisonsView.as_view(),
        name="export_public",
    ),
    path(
        "exports/all/",
        ExportPublicAllView.as_view(),
        name="export_public_all",
    ),
    path(
        "exports/polls/<str:poll_name>/proof_of_vote/",
        ExportProofOfVoteView.as_view(),
        name="export_poll_proof_of_vote",
    ),
    # Comparison API
    path(
        "users/me/comparisons/<str:poll_name>",
        ComparisonListApi.as_view(),
        name="poll_comparisons_me_list",
    ),
    path(
        "users/me/comparisons/<str:poll_name>/<str:uid>/",
        ComparisonListFilteredApi.as_view(),
        name="poll_comparisons_me_list_filtered",
    ),
    path(
        "users/me/comparisons/<str:poll_name>/<str:uid_a>/<str:uid_b>/",
        ComparisonDetailApi.as_view(),
        name="poll_comparisons_me_detail",
    ),
    # RateLater API
    path(
        "users/me/rate_later/<str:poll_name>/",
        RateLaterList.as_view(),
        name="usersme_ratelater_list",
    ),
    path(
        "users/me/rate_later/<str:poll_name>/<str:uid>/",
        RateLaterDetail.as_view(),
        name="usersme_ratelater_detail",
    ),
    # Ratings API
    path(
        "users/me/contributor_ratings/<str:poll_name>/",
        ContributorRatingList.as_view(),
        name="ratings_me_list",
    ),
    path(
        "users/me/contributor_ratings/<str:poll_name>/_all/",
        ContributorRatingUpdateAll.as_view(),
        name="ratings_me_list_update_is_public",
    ),
    path(
        "users/me/contributor_ratings/<str:poll_name>/<str:uid>/",
        ContributorRatingDetail.as_view(),
        name="ratings_me_detail",
    ),
    # Suggestions
    path(
        "users/me/suggestions/<str:poll_name>/tocompare/",
        SuggestionsToCompare.as_view(),
        name="suggestions_me_to_compare"
    ),
    # Sub-samples API
    path(
        "users/me/subsamples/<str:poll_name>/",
        SubSamplesList.as_view(),
        name="subsamples_me_detail",
    ),
    # Inconsistencies API
    path(
        "users/me/inconsistencies/length_3_cycles/<str:poll_name>",
        Length3Cycles.as_view(),
        name="length_3_cycles",
    ),
    path(
        "users/me/inconsistencies/score/<str:poll_name>",
        ScoreInconsistencies.as_view(),
        name="score_inconsistencies",
    ),
    # User recommendations API
    path(
        "users/me/recommendations/<str:poll_name>",
        PrivateContributorRecommendationsView.as_view(),
        name="private_contributor_recommendations",
    ),
    path(
        "users/<str:username>/recommendations/<str:poll_name>",
        PublicContributorRecommendationsView.as_view(),
        name="public_contributor_recommendations",
    ),
    # Unconnected entities
    path(
        "users/me/unconnected_entities/<str:poll_name>/<str:uid>/",
        UnconnectedEntitiesView.as_view(),
        name="unconnected_entities",
    ),
    # User statistics
    path(
        "users/me/criteria_correlations/<str:poll_name>/",
        ContributorCriteriaCorrelationsView.as_view(),
        name="contributor_criteria_correlations",
    ),
    # Contributors' proof API
    path(
        "users/me/proof/<str:poll_name>/",
        ProofView.as_view(),
        name="usersme-proof",
    ),
    # Email domain API
    path("domains/", EmailDomainsList.as_view(), name="email_domains_list"),
    # Statistics API
    path("stats/", StatisticsView.as_view(), name="statistics_detail"),
    # Polls API
    path("polls/<str:name>/", PollsView.as_view(), name="polls_detail"),
    path(
        "polls/<str:name>/recommendations/",
        PollsRecommendationsView.as_view(),
        name="polls_recommendations",
    ),
    path(
        "polls/<str:name>/recommendations/random/",
        RandomRecommendationList.as_view(),
        name="polls_recommendations_random",
    ),
    path(
        "polls/<str:name>/entities/<str:uid>",
        PollsEntityView.as_view(),
        name="polls_score_distribution",
    ),
    path(
        "polls/<str:name>/entities/<str:uid>/criteria_scores_distributions",
        PollsCriteriaScoreDistributionView.as_view(),
        name="polls_score_distribution",
    ),
    # Website Previews
    re_path(
        r"^preview/comparison/?$",
        DynamicWebsitePreviewComparison.as_view(),
        name="website_preview_comparison",
    ),
    path(
        "preview/entities/<str:uid>",
        DynamicWebsitePreviewEntity.as_view(),
        name="website_preview_entity",
    ),
    re_path(
        r"^preview/faq/?$",
        DynamicWebsitePreviewFAQ.as_view(),
        name="website_preview_faq",
    ),
    # This route show the preview for the recommendations page
    # after preview/recommendations route rewrite the url paramaters
    # to match backend parameters and redirect
    path(
        "preview/_recommendations/",
        DynamicWebsitePreviewRecommendations.as_view(),
        name="website_preview_recommendations_internal",
    ),
    # This route rewrite the url for the recommendations page preview
    re_path(
        r"^preview/recommendations/?$",
        get_preview_recommendations_redirect_params,
        name="website_preview_recommendations_redirect",
    ),
    re_path(
        r"^preview/.*$",
        DynamicWebsitePreviewDefault.as_view(),
        name="website_preview_default",
    ),
]
