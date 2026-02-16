from solidago import *

import logging.config

from solidago.primitives.timer import time

logging.config.fileConfig("tests/info.conf")


gbts = [
    poll_functions.NumbaUniformGBT(),
    poll_functions.LBFGSUniformGBT(),
    poll_functions.FlexibleGeneralizedBradleyTerry(discard_ratings=True),
]

def preference_learning(tiny = True):
    for gbt in gbts:
        poll = TournesolExport(f"tests/{'tiny_tournesol' if tiny else 'tournesol_dataset'}.zip")
        with time("Filtering"):
            poll = poll_functions.Filtering(usernames={"lpfaucon"}, criteria={"largely_recommended"})(poll)
        assert isinstance(gbt, (poll_functions.PollFunction)), gbt
        with time(f"Preference learning with {type(gbt).__name__}"):
            gbt.poll2poll_function(poll)


if __name__ == "__main__":
    preference_learning(tiny=False)