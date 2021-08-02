import logging
import torch

from ml.licchavi import Licchavi


""" LicchaviDev(Licchavi) class used for experiments only

Allows to use ground truths of generated data

"""


class LicchaviDev(Licchavi):
    def __init__(
            self, nb_vids, vid_vidx, crit,
            test_mode=False, device='cpu', verb=1):
        # Inits Licchavi class
        super().__init__(
            nb_vids, vid_vidx, crit,
            test_mode=test_mode, device=device, verb=verb)
        # Inits attibutes required for test_mode
        if test_mode:
            self.glob_gt = []  # global scores ground truths
            self.loc_gt = []  # local scores ground truths
            self.s_gt = []  # s parameters ground truths
            self.history['error_loc'] = []
            self.history['error_glob'] = []

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

    def _test_errors(self):
        """ Returns errors (for test mode only)

        Returns:
            (float): global mean squared distance between
                                predicted and ground truth
            (float): local mean squared distance between
                                predicted and ground truth
        """
        with torch.no_grad():
            glob_out, loc_out = self.output_scores()
            if len(glob_out[1]) != len(self.glob_gt):
                logging.error('Some videos have not been rated')
            glob_errors = (glob_out[1] - self.glob_gt)**2
            glob_mean_error = float(sum(glob_errors)) / self.nb_vids

            loc_error, nb_loc = 0, 0
            for uid, predictions in zip(self.nodes, loc_out[1]):
                for i, score_pred in zip(self.loc_gt[int(uid)], predictions):
                    score_gt = self.loc_gt[int(uid)][i]
                    loc_error += float((score_pred - score_gt)**2)
                    nb_loc += 1
            loc_mean_error = loc_error / nb_loc
        return glob_mean_error, loc_mean_error

    def _update_hist(self, epoch, fit, s, gen, reg):
        """ Updates history (at end of epoch)

        Inheriting from Licchavi._update_hist()
         """
        super()._update_hist(epoch, fit, s, gen, reg)
        # additional test mode metrics unsing ground truths
        if self.test_mode:
            factor_glob, factor_loc = 1, 1  # for visualisation only
            glob_error, loc_error = self._test_errors()
            self.history['error_glob'].append(glob_error * factor_glob)
            self.history['error_loc'].append(loc_error * factor_loc)
