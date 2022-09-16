# TO BE DELETED, just use to do some test

from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.image as mpimg
import datetime

# TODO:
# - Traduction
# - get month name from Django


def generate_top_contributor_figure() -> Path:
    """Generate a figure with the top contributor of each video."""

    # top_contributors = get_top_public_contributors_last_month(poll_name=DEFAULT_POLL_NAME, top=10)

    top_contributors = {
        "user0": 2677,
        "user1": 2556,
        "user2": 1556,
        "user3": 1556,
        "user4_too_long": 1356,
        "user4": 556,
        "user5": 456,
        "user6": 453,
        "user7": 356,
        "user8": 256,
        "u": 156,
    }

    now = datetime.datetime.now()

    last_month = now.month - 1
    year = now.year

    if last_month == 12:
        year -= 1

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
    fig, ax = plt.subplots(dpi=150)

    short_usernames = [
        name[:11] + "..." if len(name) > 13 else name
        for name in list(top_contributors.keys())
    ]

    plt.bar(
        short_usernames, list(top_contributors.values()), color="#567234", width=0.15
    )
    plt.title(
        f"Tournesol top public contributors of {MONTHS[last_month]} {year}", fontsize=14
    )
    plt.xticks(rotation=70, fontsize=10)
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
