# TO BE DELETED, just use to do some test

from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.image as mpimg
import datetime

# from tournesol.utils.contributors import get_top_public_contributors_last_month

# TODO:
# - Traduction
# - get month name from Django


def generate_top_contributor_figure() -> Path:
    """Generate a figure with the top contributor of each video."""

    # top_contributors = get_top_public_contributors_last_month(poll_name=DEFAULT_POLL_NAME, top=10)

    top_contributors = {
        "user0": 950,
        "user1": 256,
        "user2": 156,
        "user3": 156,
        "user4_very_long_name": 136,
        "user4": 56,
        "user5": 56,
        "le_science4all": 53,
        "user7": 35,
        "user8": 26,
        "u": 15,
    }

    now = datetime.datetime.now()

    last_month = now.month - 1
    year = now.year

    if last_month == 0:
        year -= 1
        last_month = 12

    MONTHS = {
        1: "January",
        2: "February",
        3: "March",
        4: "April",
        5: "May",
        6: "June",
        7: "July",
        8: "August",
        9: "September",
        10: "October",
        11: "November",
        12: "December",
    }

    # Save figure
    fig_path = Path("/tmp/top_contributor.png")

    plt.xkcd()
    plt.rcParams["font.family"] = ["Arial"]
    fig, ax = plt.subplots(dpi=150)

    short_usernames = [
        name[:13] + "..." if len(name) > 15 else name
        for name in list(top_contributors.keys())
    ]

    plt.bar(
        short_usernames, list(top_contributors.values()), color="#567234", width=0.15
    )
    plt.title(
        f"Tournesol top public contributors of {MONTHS[last_month]} {year}", fontsize=14
    )
    plt.xticks(rotation=50, ha="right", fontsize=10)
    plt.ylabel("Number of comparisons", fontsize=12)
    plt.yticks(fontsize=10)
    plt.subplots_adjust(bottom=0.22, left=0.15, right=0.95)

    # Add sunflower images
    tournesol_logo = mpimg.imread("./Logo128.png")
    imagebox = OffsetImage(tournesol_logo, zoom=0.18)

    for top_pos, nb_rating in enumerate(top_contributors.values()):
        ab = AnnotationBbox(imagebox, (top_pos, nb_rating), frameon=False)
        ax.add_artist(ab)

    plt.savefig("test_top_contributor.png", dpi=150)
    plt.show()

    return fig_path

generate_top_contributor_figure()
