# Quality criteria
MIN_NB_CONTRIBUTORS = 5
MIN_NB_RATINGS = 15
MIN_RELIABILITY_SCORE = 10
MIN_TOURNESOL_SCORE = 10

# Date range for videos to be considered
DAYS_TOO_RECENT = 7  # min 1 week old
DAYS_TOO_OLD = 210  # max 7 months old

# Number of days to wait before tweeting the same uploader again
DAYS_ALREADY_TWEETED_UPLOADER = 7

# Daily tweet text template
tweet_text_template = {
    "en": (
        "Today, I recommend '{title}' by {twitter_account}"
        ", compared {n_comparison} times on #Tournesol\U0001F33B by {n_contributor}"
        " contributors, favorite criteria:\n- {crit1}\n- {crit2}\n"
        "tournesol.app/entities/yt:{video_id}"
    ),
    "fr": (
        "Aujourd'hui, je recommande '{title}' de {twitter_account}"
        ", comparée {n_comparison} fois sur #Tournesol\U0001F33B par {n_contributor}"
        " contributeurs, critères favoris:\n- {crit1}\n- {crit2}\n"
        "tournesol.app/entities/yt:{video_id}"
    ),
}

# Name of the Discord channel where the twitterbot will post its tweets.
# An empty value won't trigger any post.
TWITTERBOT_DISCORD_CHANNEL = "twitter"
