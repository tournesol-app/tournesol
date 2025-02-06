import random
import re
import tempfile
from datetime import timedelta
from pathlib import Path
from typing import Literal

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from django.utils import dateformat, timezone, translation
from matplotlib.offsetbox import AnnotationBbox, OffsetImage

from core.lib.discord.api import write_in_channel
from core.utils.time import time_ago
from tournesol.models import Entity
from tournesol.models.criteria import CriteriaLocale
from tournesol.models.entity_score import ScoreMode
from tournesol.models.poll import DEFAULT_POLL_NAME, Poll
from tournesol.utils.contributors import get_top_public_contributors_last_month
from twitterbot import settings
from twitterbot.client import TournesolBotClient
from twitterbot.models.history import TweetInfo
from twitterbot.uploader_twitter_account import get_twitter_account_from_video_id


def get_video_short_url(video: Entity):
    return f"tournesol.app/entities/{video.uid}"


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


def prepare_text(video: Entity, dest: Literal["twitter", "bluesky"]):
    """Create the tweet text from the video."""

    uploader = video.metadata["uploader"]
    language = video.metadata["language"]
    video_id = video.metadata["video_id"]

    # Get twitter account
    if dest == "twitter":
        channel_handle = get_twitter_account_from_video_id(video_id)
    else:
        channel_handle = None
        # TODO: implement fetch Bluesky handle
        # twitter_account = get_bluesky_handle_from_video_id(video_id)

    if not channel_handle:
        channel_handle = f"'{uploader}'"

    # Get two best criteria and criteria dict name
    crit1, crit2 = get_best_criteria(video, 2)
    crit_dict = dict(
        CriteriaLocale.objects.filter(language=language).values_list("criteria__name", "label")
    )

    video_title = video.metadata["name"]
    if dest == "twitter":
        # Replace "@" by a smaller "@" to avoid false mentions in the tweet
        video_title = video_title.replace("@", "﹫")

        # Replace "." in between words to avoid in the tweet false detection of links
        video_title = re.sub(r"\b(?:\.)\b", "․", video_title)

    # Generate the text of the tweet
    poll_rating = video.all_poll_ratings.get(poll__name=DEFAULT_POLL_NAME)
    tweet_text = settings.tweet_text_template[language].format(
        title=video_title,
        twitter_account=channel_handle,
        n_comparison=poll_rating.n_comparisons,
        n_contributor=poll_rating.n_contributors,
        crit1=crit_dict[crit1[0]],
        crit2=crit_dict[crit2[0]],
        video_id=video_id,
    )

    # Check the total length of the tweet and shorten title if the tweet is too long
    # 250 is used because the link will be counted as 23 characters, which leaves
    # a margin of error for emoji which are counted as 2 characters before reaching
    # the limit of 280 characters.
    diff = len(tweet_text) - 250
    if diff > 0:
        video_title = video_title[: -diff - 1] + "…"
        tweet_text = settings.tweet_text_template[language].format(
            title=video_title,
            twitter_account=channel_handle,
            n_comparison=poll_rating.n_comparisons,
            n_contributor=poll_rating.n_contributors,
            crit1=crit_dict[crit1[0]],
            crit2=crit_dict[crit2[0]],
            video_id=video_id,
        )

    if dest != "bluesky":
        # on Bluesky the URL preview is attached separately as "embed"
        tweet_text += f"\n{get_video_short_url(video)}"

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
    tweetable_videos = (
        Entity
        .objects
        .filter_safe_for_poll(Poll.default_poll())
        .with_prefetched_poll_ratings(poll_name=DEFAULT_POLL_NAME)
        .filter(
            add_time__lte=time_ago(days=settings.DAYS_TOO_RECENT),
            metadata__publication_date__gte=time_ago(days=settings.DAYS_TOO_OLD).isoformat(),
            metadata__language=language,
            all_poll_ratings__n_contributors__gt=settings.MIN_NB_CONTRIBUTORS,
            all_poll_ratings__n_comparisons__gte=settings.MIN_NB_RATINGS,
            all_poll_ratings__tournesol_score__gte=settings.MIN_TOURNESOL_SCORE,
            pk__in=reliable_videos,
            tweets=None,
        )
    )

    # Exclude video recently tweeted by the same uploader
    exclude_uploader = TweetInfo.objects.filter(
        datetime_tweet__gte=time_ago(days=settings.DAYS_ALREADY_TWEETED_UPLOADER)
    ).values("video__metadata__uploader")

    tweetable_videos = tweetable_videos.exclude(metadata__uploader__in=exclude_uploader)

    return list(tweetable_videos)


def select_a_video(tweetable_videos):
    """Select a video to tweet."""

    tournesol_score_list = [
        v.single_poll_rating.tournesol_score
        for v in tweetable_videos
    ]

    # Chose a random video weighted by tournesol score
    selected_video = random.choices(  # not a cryptographic use # nosec B311
        tweetable_videos, weights=tournesol_score_list
    )[0]

    return selected_video


def tweet_video_recommendation(bot_name, dest: list[str], assumeyes=False):
    """Tweet a video recommendation.

    Args:
        bot_name (str): The name of the bot.
        assumeyes (bool): If False, a confirmation will be asked before tweeting it.
        dest (list[str]): List of destinations where to post the message
            Accepted values are "twitter" and "bluesky".
    """

    bot_client = TournesolBotClient(bot_name)

    tweetable_videos = get_video_recommendations(language=bot_client.language)
    if not tweetable_videos:
        print("No video reach the criteria to be tweeted today!!!")
        return

    video = select_a_video(tweetable_videos)

    print("Today's video to post will be:")
    print(f"{video} '{video.metadata['name']}' by {video.metadata['uploader']}")

    if not assumeyes:
        confirmation = input("\nWould you like to tweet that? (y/n): ")
        if confirmation not in ["y", "yes"]:
            return

    tweet_id = None
    atproto_uri = None
    # Tweet the video
    if "twitter" in dest:
        tweet_text = prepare_text(video, dest="twitter")
        tweet_id = bot_client.create_tweet(text=tweet_text)

    if "bluesky" in dest:
        text = prepare_text(video, dest="bluesky")
        atproto_uri = bot_client.create_bluesky_post(text=text, embed_video=video)

    # Add the video to the TweetInfo table
    tweet_info: TweetInfo = TweetInfo.objects.create(
        video=video,
        tweet_id=tweet_id,
        atproto_uri=atproto_uri,
        bot_name=bot_name,
    )

    # Post the tweet on Discord
    discord_channel = settings.TWITTERBOT_DISCORD_CHANNEL
    if discord_channel:
        write_in_channel(discord_channel, message=tweet_info.message_url)


def generate_top_contributor_figure(top_contributors_qs, language="en") -> Path:
    """Generate a figure with the top contributor of each video."""

    last_month_dt = timezone.now().replace(day=1) - timedelta(days=1)
    year = last_month_dt.year

    if language in ["en", "fr"]:
        with translation.override(language):
            month_name = dateformat.format(last_month_dt, "F")
    else:
        raise ValueError("Language not found!")

    figure_path = (
        Path(tempfile.gettempdir()) / f"top_contributor_{month_name}_{year}_{language}.png"
    )

    plt.xkcd()
    plt.rcParams["font.family"] = ["sans-serif"]
    _fig, axes = plt.subplots(dpi=150)

    short_usernames = [
        name[:12] + "…" if len(name) > 14 else name
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
    plt.xticks(rotation=42, ha="right", fontsize=9)
    plt.yticks(fontsize=10)
    plt.ylabel(settings.graph_ylabel_text_template[language], fontsize=12)
    plt.subplots_adjust(bottom=0.22, left=0.15, right=0.95)

    logo_path = Path(__file__).parents[1] / "tournesol" / "resources" / "Logo128.png"
    tournesol_logo = mpimg.imread(logo_path)
    imagebox = OffsetImage(tournesol_logo, zoom=0.18)

    for top_pos, nb_rating in enumerate(u.n_comparisons for u in top_contributors_qs):
        axes.add_artist(AnnotationBbox(imagebox, (top_pos, nb_rating), frameon=False))

    plt.savefig(figure_path, dpi=300)

    return figure_path


def tweet_top_contributor_graph(bot_name, dest: Literal["twitter", "bluesky"], assumeyes=False):
    """Tweet the top contibutor graph of last month.

    Args:
        bot_name (str): The name of the bot.
        assumeyes (bool): If True, a confirmation will be asked before tweeting it.

    """

    bot_client = TournesolBotClient(bot_name)
    language = bot_client.language

    top_contributors_qs = get_top_public_contributors_last_month(
        poll_name=DEFAULT_POLL_NAME, top=10
    )
    top_contributor_figure = generate_top_contributor_figure(top_contributors_qs, language)

    if not top_contributor_figure.exists():
        print("The top contributor graph has not been generated")
        return

    if not assumeyes:
        confirmation = input(
            f"\nThe image has been generated in {top_contributor_figure}\n"
            "Would you like to tweet this image? (y/n): "
        )
        if confirmation not in ["y", "yes"]:
            return

    message_url = None
    if "twitter" in dest:
        tweet_id = bot_client.create_tweet(
            text=settings.top_contrib_tweet_text_template[language],
            media_files=[top_contributor_figure]
        )
        message_url = f"https://twitter.com/{bot_name}/status/{tweet_id}"

    if "bluesky" in dest:
        post_uri = bot_client.create_bluesky_post(
            text=settings.top_contrib_tweet_text_template[language],
            image_files=[top_contributor_figure],
            image_alts=[settings.top_contrib_tweet_image_alt[language]]
        )
        post_id = post_uri.rsplit("/", 1)[-1]
        message_url = f'https://bsky.app/profile/{bot_client.bluesky_handle}/post/{post_id}'

    if message_url is not None:
        # Post the tweet on Discord
        discord_channel = settings.TWITTERBOT_DISCORD_CHANNEL
        if discord_channel:
            write_in_channel(
                discord_channel,
                message=message_url,
            )
