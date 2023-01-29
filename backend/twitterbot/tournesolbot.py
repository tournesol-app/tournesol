from datetime import timedelta
import random
import re
from pathlib import Path
from django.utils import timezone, translation
from django.utils.dateformat import format

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnnotationBbox, OffsetImage

from core.utils.time import time_ago
from tournesol.models import Entity
from tournesol.models.criteria import CriteriaLocale
from tournesol.models.entity_score import ScoreMode
from tournesol.models.poll import DEFAULT_POLL_NAME
from tournesol.utils.contributors import get_top_public_contributors_last_month
from twitterbot import settings
from twitterbot.models.tweeted import TweetInfo
from twitterbot.twitter_api import TwitterBot
from twitterbot.uploader_twitter_account import get_twitter_account_from_video_id


def get_best_criteria(video, nb_criteria):
    """Get the nb_criteria best-rated criteria"""

    criteria_list = (
        video.all_criteria_scores.filter(
            poll__name=DEFAULT_POLL_NAME,
            score_mode=ScoreMode.DEFAULT,
        )
        .exclude(criteria="largely_recommended")
        .order_by("-score")[:nb_criteria]
    )

    if len(criteria_list) < nb_criteria:
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
        CriteriaLocale.objects.filter(language=language).values_list(
            "criteria__name", "label"
        )
    )

    # Replace "@" by a smaller "@" to avoid false mentions in the tweet
    video_title = video.metadata["name"].replace("@", "﹫")

    # Replace "." in between words to avoid in the tweet false detection of links
    video_title = re.sub(r"\b(?:\.)\b", "․", video_title)

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
    # 288 is used because the link will be count as 23 characters and not 37 so 274 which leaves
    # a margin of error for emoji which are counted as 2 characters
    diff = len(tweet_text) - 288
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
        metadata__publication_date__gte=time_ago(
            days=settings.DAYS_TOO_OLD
        ).isoformat(),
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

    selected_video = random.choices(  # not a cryptographic use # nosec B311
        tweetable_videos, weights=tournesol_score_list
    )[0]

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

    # Post the tweet on Discord
    discord_channel = settings.TWITTERBOT_DISCORD_CHANNEL
    if discord_channel:
        write_in_channel(
            discord_channel,
            f"https://twitter.com/{bot_name}/status/{resp.id}",
        )

    # Add the video to the TweetInfo table
    TweetInfo.objects.create(
        video=video,
        tweet_id=resp.id,
        bot_name=bot_name,
    )


def generate_top_contributor_figure(language="en") -> Path:
    """Generate a figure with the top contributor of each video."""

    last_month_dt = timezone.now().replace(day=1) - timedelta(days=1)
    year = last_month_dt.year

    if language == "en":
        month_name = format(last_month_dt, "F")
    elif language == "fr":
        with translation.override("fr"):
            month_name = format(last_month_dt, "F")
    else:
        raise ValueError("Language not found!")

    top_contributors_qs = get_top_public_contributors_last_month(
        poll_name=DEFAULT_POLL_NAME, top=10
    )

    fig_path = Path("/tmp/top_contributor.png")

    plt.xkcd()
    plt.rcParams["font.family"] = ["sans-serif"]
    fig, ax = plt.subplots(dpi=150)

    short_usernames = [
        name[:13] + "..." if len(name) > 15 else name
        for name in (u.username for u in top_contributors_qs)
    ]

    plt.bar(
        short_usernames,
        [u.n_comparisons for u in top_contributors_qs],
        color="#567234",
        width=0.15,
    )
    graph_title = settings.graph_title_text_template[language].format(
        month_name=month_name,
        year=year,
    )
    plt.title(graph_title, fontsize=14)
    plt.xticks(rotation=50, ha="right", fontsize=10)
    plt.yticks(fontsize=10)
    plt.ylabel(settings.graph_ylabel_text_template[language], fontsize=12)
    plt.subplots_adjust(bottom=0.22, left=0.15, right=0.95)

    logo_path = Path(__file__).parent / "Logo128.png"
    tournesol_logo = mpimg.imread(logo_path)
    imagebox = OffsetImage(tournesol_logo, zoom=0.18)

    for top_pos, nb_rating in enumerate(u.n_comparisons for u in top_contributors_qs):
        ab = AnnotationBbox(imagebox, (top_pos, nb_rating), frameon=False)
        ax.add_artist(ab)

    plt.savefig(fig_path, dpi=300)
    plt.show()

    return fig_path
