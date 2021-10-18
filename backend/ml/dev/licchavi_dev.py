""" LicchaviDev(Licchavi) class used for experiments only

Allows to use ground truths of generated data

"""
import logging

from ml.core import TOURNESOL_DEV
from ml.licchavi import Licchavi

if not TOURNESOL_DEV:
    raise Exception('Dev module called whereas TOURNESOL_DEV=0')


class LicchaviDev(Licchavi):
    """ Licchavi class for development experiments """
    def __init__(
            self, nb_vids, vid_vidx, crit,
            test_mode=False, device='cpu', verb=1):
        """
        nb_vids (int): number of different videos rated by
                        at least one contributor for this criteria
        vid_vidx (dictionnary): dictionnary of {video ID: video index}
        crit (str): comparison criteria learnt
        test_mode (bool): wether we use fake data or not
        device (str): device used (cpu/gpu)
        verb (float): verbosity level
        """
        # Inits Licchavi class
        super().__init__(nb_vids, vid_vidx, crit, device=device, verb=verb)

        self.test_mode = test_mode
        # Inits attributes required for test_mode
        if test_mode:
            self.glob_gt = []  # global scores ground truths
            self.loc_gt = []  # local scores ground truths
            self.s_gt = []  # s parameters ground truths
            self.history_loc['error_loc'] = []
            self.history_glob['error_glob'] = []

    def set_ground_truths(self, glob_gt, loc_gt, s_gt):
        """ Puts ground truths in Licchavi (for experiments only)

        glob_gt (float array): generated global scores
        loc_gt (list of list of couples): (vid, local score) for each video
                                                            of each node
        """
        if not self.test_mode:
            logging.warning('Not in test mode')
        self.glob_gt = glob_gt
        self.loc_gt = [dict(node) for node in loc_gt]
        self.s_gt = s_gt
