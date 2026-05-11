from solidago import *

import logging.config

from solidago.primitives.timer import time

logging.config.fileConfig("tests/info.conf")


gbts = [
    functions.preference_learning.numba_generalized_bradley_terry.NumbaUniformGBT(),
    functions.preference_learning.lbfgs_generalized_bradley_terry.LBFGSUniformGBT(),
    functions.preference_learning.FlexibleGeneralizedBradleyTerry(discard_ratings=True),
]

def preference_learning(tiny = True):
    for gbt in gbts:
        poll = TournesolExport(f"tests/{'tiny_tournesol' if tiny else 'tournesol_dataset'}.zip")
        kwargs = dict(usernames={"lpfaucon"}, criteria={"largely_recommended"})
        with time("Filtering"):
            poll = functions.filtering.Filtering(**kwargs).fn(poll)
        assert isinstance(gbt, (functions.PollFunction)), gbt
        with time(f"Preference learning with {type(gbt).__name__}"):
            gbt(poll)


if __name__ == "__main__":
    preference_learning(tiny=False)