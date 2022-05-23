import random

from core.utils.time import time_ago
from tournesol.models import Entity
from tournesol.models.criteria import CriteriaLocale
from tournesol.models.entity_score import ScoreMode
from tournesol.models.poll import DEFAULT_POLL_NAME
from twitterbot import settings
from twitterbot.models.tweeted import TweetInfo
from twitterbot.twitter_api import TwitterBot
from twitterbot.uploader_twitter_account import get_twitter_account_from_video_id


def get_best_criteria(video, n):
    """Get the n best criteria"""

    criteria_list = (
        video.all_criteria_scores.filter(
            poll__name=DEFAULT_POLL_NAME,
            score_mode=ScoreMode.DEFAULT,
        )
        .exclude(criteria="largely_recommended")
        .order_by("-score")[:n]
    )

    if len(criteria_list) < n:
        raise ValueError("Not enough criteria to show!")

    return [(crit.criteria, crit.score) for crit in criteria_list]


def prepare_tweet(video):
    """Create the tweet text from the video."""

    uploader = video.metadata["uploader"]
    language = video.metadata["language"]
    video_id = video.metadata["video_id"]

    # Get twitter account
    twitter_account = get_twitter_account_from_video_id(video_id)

    if not twitter_account:
        twitter_account = f"'{uploader}'"

    # Get two best criteria and criteria dict name
    crit1, crit2 = get_best_criteria(video, 2)
    crit_dict = dict(
        CriteriaLocale.objects.filter(language=language).values_list("criteria__name", "label")
    )

    # Replace "@" by "at" to avoid false mentions in the tweet
    video_title = video.metadata["name"].replace("@", "at")

    # Generate the text of the tweet
    tweet_text = settings.tweet_text_template[language].format(
        title=video_title,
        twitter_account=twitter_account,
        n_comparison=video.rating_n_ratings,
        n_contributor=video.rating_n_contributors,
        crit1=crit_dict[crit1[0]],
        crit2=crit_dict[crit2[0]],
        video_id=video_id,
    )

    # Check the total length of the tweet and shorten title if the tweet is too long
    # 274 is used to get a margin of error (emoji may be counted as 2 chars)
    diff = len(tweet_text) - 274
    if diff > 0:
        video_title = video_title[: -diff - 3] + "..."

        tweet_text = settings.tweet_text_template[language].format(
            title=video_title,
            twitter_account=twitter_account,
            n_comparison=video.rating_n_ratings,
            n_contributor=video.rating_n_contributors,
            crit1=crit_dict[crit1[0]],
            crit2=crit_dict[crit2[0]],
            video_id=video_id,
        )

    return tweet_text


def get_video_recommendations(language):
    """Find a list of good video to recommend with some quality criteria."""

    reliable_videos = Entity.objects.filter(
        all_criteria_scores__poll__name=DEFAULT_POLL_NAME,
        all_criteria_scores__score_mode=ScoreMode.DEFAULT,
        all_criteria_scores__criteria="reliability",
        all_criteria_scores__score__gt=settings.MIN_RELIABILITY_SCORE,
    )

    # Filter videos with some quality criteria
    tweetable_videos = Entity.objects.filter(
        add_time__lte=time_ago(days=settings.DAYS_TOO_RECENT),
        metadata__publication_date__gte=time_ago(days=settings.DAYS_TOO_OLD).isoformat(),
        rating_n_contributors__gt=settings.MIN_NB_CONTRIBUTORS,
        rating_n_ratings__gte=settings.MIN_NB_RATINGS,
        metadata__language=language,
        tournesol_score__gte=settings.MIN_TOURNESOL_SCORE,
        pk__in=reliable_videos,
        tweets=None,
    )

    # Exclude video recently tweeted by the same uploader
    exclude_uploader = TweetInfo.objects.filter(
        datetime_tweet__gte=time_ago(days=settings.DAYS_ALREADY_TWEETED_UPLOADER)
    ).values("video__metadata__uploader")

    tweetable_videos = tweetable_videos.exclude(metadata__uploader__in=exclude_uploader)

    return list(tweetable_videos)


def select_a_video(tweetable_videos):
    """Select a video to tweet."""

    tournesol_score_list = [v.tournesol_score for v in tweetable_videos]

    # Chose a random video weighted by tournesol score
    selected_video = random.choices(tweetable_videos, weights=tournesol_score_list)[0]

    return selected_video


def tweet_video_recommendation(bot_name, assumeyes=False):
    """Tweet a video recommendation.

    Args:
        bot_name (str): The name of the bot.
        debug (bool): If True, a confirmation will be asked before tweeting it.

    """

    twitterbot = TwitterBot(bot_name)
    twitterbot.authenticate()

    tweetable_videos = get_video_recommendations(language=twitterbot.language)
    if not tweetable_videos:
        print("No video reach the criteria to be tweeted today!!!")
        return

    video = select_a_video(tweetable_videos)
    tweet_text = prepare_tweet(video)

    print("Today's video to tweet will be:")
    print(tweet_text)

    if not assumeyes:
        confirmation = input("\nWould you like to tweet that? (y/n): ")
        if confirmation not in ["y", "yes"]:
            return

    # Tweet the video
    resp = twitterbot.api.update_status(tweet_text)

    # Add the video to the TweetInfo table
    TweetInfo.objects.create(
        video=video,
        tweet_id=resp.id,
        bot_name=bot_name,
    )
