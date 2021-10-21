"""
Machine Learning algorithm, used in "core.py"
ML model and decentralised structure are here

Structure:
- Licchavi class is the structure designed to include
    a global model and one for each node
-- read Licchavi __init__ comments to better understand

Usage:
- hardcode training hyperparameters in "hyperparameters.py"
- use Licchavi.set_allnodes() to populate nodes
- use Licchavi.train() to train the models
- use Licchavi.output_scores() to get the results
"""

import logging
from logging import info as loginf
from time import time
import torch
import gin

from .losses import (round_loss, predict, loss_fit, loss_s_gen_reg)
from .metrics import (
    get_uncertainty_loc, get_uncertainty_glob, update_hist,
    check_equilibrium_glob, check_equilibrium_loc)
from .data_utility import expand_tens, one_hot_vids
from .nodes import Node


def get_model(nb_vids, device='cpu', bias_init=0):
    """ Returns an initialized scoring model """
    if bias_init:
        model = torch.ones(nb_vids, device=device) * bias_init
        model.requires_grad = True
        return model
    return torch.zeros(nb_vids, requires_grad=True, device=device)


def get_t(device='cpu'):
    """ Returns an initialized t (translation) parameter """
    return torch.zeros(1, requires_grad=True, device=device)


def get_s(device='cpu'):
    """ Returns an initialized s (scaling) parameter """
    return torch.ones(1, requires_grad=True, device=device)


@gin.configurable
class Licchavi():
    """ Training structure including local models and general one """
    def __init__(
            self,
            nb_vids,
            vid_vidx,
            crit,
            device='cpu',
            verb=1,
            # configured with gin in "hyperparameters.gin"
            metrics_loc=None,
            metrics_glob=None,
            lr_loc=None,
            lr_t=None,
            lr_s=None,
            lr_glob=None,
            nu_par=None,
            w0_par=None,
            w_loc=None,
            gamma=None,
            ):
        """
        nb_vids (int): number of different videos rated by
                        at least one contributor for this criteria
        vid_vidx (dictionnary): dictionnary of {video ID: video index}
        crit (str): comparison criteria learnt
        device (str): device used (cpu/gpu)
        verb (float): verbosity level
        """
        self.verb = verb
        self.nb_vids = nb_vids  # number of parameters of the model
        self.vid_vidx = vid_vidx  # {video ID : video index}
        self.criteria = crit  # criteria learnt by this Licchavi
        self.device = device  # device used (cpu/gpu)

        self.opt = torch.optim.SGD   # optimizer

        # defined in "hyperparameters.gin"
        self.lr_loc = lr_loc    # local learning rate (local scores)
        self.lr_t = lr_t  # local learning rate for t parameter
        self.lr_s = lr_s     # local learning rate for s parameter
        self.lr_glob = lr_glob  # global learning rate (global scores)
        self.nu_par = nu_par  # importance of s_loss term
        self.w0_par = w0_par     # regularisation strength
        self.w_loc = w_loc   # default weight for a node
        self.gamma = gamma  # local regularisation term

        self.get_model = get_model  # neural network to use
        self.global_model = self.get_model(nb_vids, device)
        self.opt_gen = self.opt([self.global_model], lr=self.lr_glob)

        self.nb_nodes = 0
        self.nodes = {}
        self.users = []  # users IDs

        # history stuff
        self.history_loc = {metric: [] for metric in metrics_loc}
        self.history_glob = {metric: [] for metric in metrics_glob}
        comparative_metrics = ['diff_loc', 'diff_glob', 'diff_s', 'grad_sp']
        self.last_epoch_loc = {
            metric: None for metric in comparative_metrics
            if metric in metrics_loc
        }
        self.last_epoch_glob = {
            metric: None for metric in comparative_metrics
            if metric in metrics_glob
        }

    def _show(self, msg, level):
        """ Utility for handling logging messages

        msg (str): info message
        level (float): minimum level of verbosity to show -msg
        """
        if self.verb >= level:
            loginf(msg)

    # ------------ input and output --------------------
    def _get_default(self):
        """ Returns: - (default s, default model) """
        model_plus = (
            get_t(self.device),  # translation parameter
            get_s(self.device),  # scaling parameter
            self.get_model(self.nb_vids, self.device),  # model
        )
        return model_plus

    def _get_saved(self, loc_models_old, uid, nb_new):
        """ Returns saved parameters updated or default

        loc_models_old (dictionnary): saved parameters in dictionnary of tuples
                                        {user ID: (t, s, model)}
        uid (int): ID of node (user)
        nb_new (int): number of new videos (since save)

        Returns:
            (t, s, model), updated or default
        """
        if uid in loc_models_old:
            t_par, s_par, mod = loc_models_old[uid]
            mod = expand_tens(mod, nb_new, self.device)
            infos = (t_par, s_par, mod)
        else:
            infos = self._get_default()
        return infos

    def set_allnodes(self, data_dic, users_ids):
        """ Puts data in Licchavi and create a model for each node

        data_dic (dictionnary): {userID: (vID1_batch, vID2_batch,
                                            rating_batch, single_vIDs, masks)}
        users_ids (int array): users IDs
        """
        self.nb_nodes = len(data_dic)
        self.users = users_ids
        self.nodes = {id: Node(
            *data,
            *self._get_default(),
            self.w_loc,
            self.lr_loc,
            self.lr_t,
            self.lr_s,
            self.opt
        ) for id, data in zip(users_ids, data_dic.values())}
        self._show("Total number of nodes : {}".format(self.nb_nodes), 1)

    def load_and_update(self, data_dic, user_ids, fullpath):
        """ Loads models and expands them as required

        data_dic (dictionnary):  {userID: (vID1_batch, vID2_batch,
                                    rating_batch, single_vIDs, masks)}
        user_ids (int array): users IDs
        """
        loginf('Loading models')
        saved_data = torch.load(fullpath)
        self.criteria, dic_old, gen_model_old, loc_models_old = saved_data
        nb_new = self.nb_vids - len(dic_old)  # number of new videos
        # initialize scores for new videos
        self.global_model = expand_tens(gen_model_old, nb_new, self.device)
        self.opt_gen = self.opt([self.global_model], lr=self.lr_glob)
        self.users = user_ids
        nbn = len(user_ids)
        self.nb_nodes = nbn
        self.nodes = {
            id: Node(
                *data,
                *self._get_saved(loc_models_old, id, nb_new),
                self.w_loc,
                self.lr_loc,
                self.lr_t,
                self.lr_s,
                self.opt
               ) for id, data in zip(user_ids, data_dic.values())
        }
        self._show(f"Total number of nodes : {self.nb_nodes}", 1)
        loginf('Models updated')

    def output_scores(self):
        """ Returns video scores both global and local

        Returns :
        - (tensor of all vIDS , tensor of global video scores)
        - (list of tensor of local vIDs, list of tensors of local video scores)
        """
        loc_scores = []
        list_vids_batchs = []

        with torch.no_grad():
            glob_scores = self.global_model
            for node in self.nodes.values():
                entry = one_hot_vids(self.vid_vidx, node.vids, self.device)
                output = predict(entry, node.model)
                loc_scores.append(output)
                list_vids_batchs.append(node.vids)
            vids_batch = list(self.vid_vidx.keys())

        return (vids_batch, glob_scores), (list_vids_batchs, loc_scores)

    def save_models(self, fullpath):
        """ Saves global and local parameters, detached (no gradients) """
        loginf('Saving models')
        local_data = {id:  (node.t_par,  # FIXME detach?
                            node.s_par,  # FIXME detach?
                            node.model.detach(),
                            ) for id, node in self.nodes.items()}
        saved_data = (
            self.criteria,
            self.vid_vidx,
            self.global_model.detach(),
            local_data
        )
        torch.save(saved_data, fullpath)
        loginf('Models saved')

    # --------- utility --------------
    def all_nodes(self, key):
        """ Returns a generator of one parameter for all nodes """
        for node in self.nodes.values():
            yield getattr(node, key)

    def _detach_loc(self):
        """ detach local models tensors (removes gradients) """
        for node in self.nodes.values():
            _ = node.model.detach_()

    # ---------- methods for training ------------
    def _set_lr(self):
        """ Sets learning rates of optimizers """
        for node in self.nodes.values():
            node.opt.param_groups[0]['lr'] = self.lr_loc  # node optimizer
            # FIXME update lr_s, lr_t (not useful currently)
        self.opt_gen.param_groups[0]['lr'] = self.lr_glob

    @gin.configurable
    def _lr_schedule(
            self, epoch,
            # configured with gin in "hyperparameters.gin"
            decay_rush=None, decay_fine=None,
            precision=None, epsilon=None,
            min_lr_fine=None, lr_rush_duration=None):
        """ Changes learning rates in a (hopefully) smart way

        epoch (int): current epoch
        verb (int): verbosity level

        Returns:
            (bool): True for an early stopping
        """

        # phase 1  : rush (high lr to increase l2 norm fast)
        if epoch <= lr_rush_duration:
            self.lr_glob *= decay_rush
            self.lr_loc *= decay_rush
        # phase 2 : fine tuning (low lr), we monitor equilibrium for early stop
        elif epoch % 2 == 0:
            if self.lr_loc >= min_lr_fine / decay_fine:
                self.lr_glob *= decay_fine
                self.lr_loc *= decay_fine
            frac_glob = check_equilibrium_glob(epsilon, self)
            self._show(f'Global eq({epsilon}): {round(frac_glob, 3)}', 1)
            if frac_glob > precision:
                frac_loc = check_equilibrium_loc(epsilon, self)
                self._show(f'Local eq({epsilon}): {round(frac_loc, 3)}', 1)
                if frac_loc > precision:
                    loginf('Early Stopping')
                    return True
        return False

    def _zero_opt(self):
        """ Sets gradients of all models """
        for node in self.nodes.values():
            node.opt.zero_grad(set_to_none=True)  # node model optimizer
            node.opt_t_s.zero_grad(set_to_none=True)  # node params optimizer
        self.opt_gen.zero_grad(set_to_none=True)  # general optimizer

    def _do_step(self, local_epoch):
        """ Makes step for appropriate optimizer(s) """
        if local_epoch:  # updating local or global alternatively
            for node in self.nodes.values():
                node.opt.step()  # node model optimizer
        else:
            for node in self.nodes.values():
                node.opt_t_s.step()  # node parameters optimizer
            self.opt_gen.step()

    def _regul_s(self):
        """ regulate s parameters """
        for node in self.nodes.values():
            if node.s_par <= 0:
                with torch.no_grad():
                    node.s_par[0] = 0.0001
                    logging.warning('Regulating negative s')

    def _print_losses(self, tot, fit, s_par, gen, reg):
        """ Prints losses into log info """
        fit, s_par = round_loss(fit, 2), round_loss(s_par, 2)
        gen, reg = round_loss(gen, 2), round_loss(reg, 2)

        loginf(
            f'total loss : {tot}\nfitting : {fit}, '
            f's : {s_par}, generalisation : {gen}, regularisation : {reg}'
        )

    # ====================  TRAINING ==================
    def _do_epoch(self, epoch, nb_epochs, local_epoch, reg_loss):
        """ Trains for one epoch

        epoch (int): current epoch
        nb_epochs (int): (maximum) number of epochs
        local_epoch (bool): True if local step, False if global step
        reg_loss (float tensor): regulation term of loss

        Returns:
            (float tensor): regulation term of loss (actualized)
        """
        self._show("epoch {}/{}".format(epoch, nb_epochs), 1)
        time_ep = time()

        fit_loss, s_loss, gen_loss = 0, 0, 0
        self._zero_opt()  # resetting gradients

        # ----------------    Licchavi loss  -------------------------
        # only local loss computed
        if local_epoch:
            fit_loss = loss_fit(self)
            loss = fit_loss

        # only global loss computed
        else:
            s_loss, gen_loss, reg_loss = loss_s_gen_reg(self)
            loss = s_loss + gen_loss + reg_loss

        # Gradient descent
        loss.backward()
        self._do_step(local_epoch)

        update_hist(
            self, local_epoch,
            (fit_loss, s_loss, gen_loss, reg_loss, epoch)
        )
        self._show(f'epoch time :{round(time() - time_ep, 2)}', 1.5)
        return reg_loss  # FIXME remove

    def train_loc(self, nb_epochs=1, compute_uncertainty=False):
        """ local training loop

        nb_epochs (int): (maximum) number of training epochs
        compute_uncertainty (bool): wether to compute uncertainty
            at the end or not (takes time)

        Returns:
            (float list list): uncertainty of local scores,None if not computed
        """
        reg_loss = 0

        # local training loop
        loginf('Starting local training')
        time_train_loc = time()
        for epoch in range(1, nb_epochs + 1):
            # self._set_lr()  # FIXME design lr scheduling
            reg_loss = self._do_epoch(epoch, nb_epochs, True, reg_loss)
        # equi = check_equilibrium_loc(0.1, self)  # FIXME use
        loginf('End of local training\n'
               f'Training time: {round(time() - time_train_loc, 2)}')

        if compute_uncertainty:  # FIXME make separate method ?
            time_uncert = time()
            uncert_loc = get_uncertainty_loc(self)
            loginf(f'Local uncertainty time: {time() - time_uncert}')
            return uncert_loc
        return None  # if uncertainty not computed

    def train_glob(self, nb_epochs=1, compute_uncertainty=False):
        """ training loop

        nb_epochs (int): (maximum) number of training epochs
        compute_uncertainty (bool): wether to compute uncertainty
            at the end or not (takes time)

        Returns:
            (float tensor) : uncertainty of global scores
                                            None if not computed
        """
        self._detach_loc()  # removing local models gradients (not needed here)
        reg_loss = 0

        # global training loop
        loginf('Starting global training')
        time_train_glob = time()
        for epoch in range(1, nb_epochs + 1):
            # self._set_lr()  # FIXME design lr scheduling
            self._regul_s()
            reg_loss = self._do_epoch(epoch, nb_epochs, False, reg_loss)
        # equi = check_equilibrium_glob(0.1, self) FIXME use
        loginf('End of global training\n'
               f'Training time: {round(time() - time_train_glob, 2)}')

        if compute_uncertainty:  # FIXME make separate method ?
            time_uncert = time()
            uncert_glob = get_uncertainty_glob(self)
            loginf(f'Global uncertainty time: {time() - time_uncert}')
            return uncert_glob
        return None  # if uncertainty not computed

    # ------------ to check for problems --------------------------
    def check(self):
        """ Performs some tests on internal parameters adequation """
        # population check
        bool1 = (self.nb_nodes == len(self.nodes))
        # history check
        reference = list(self.history_loc.values())[0]
        bool2 = all(
            len(v) == len(reference) for v in self.history_loc.values()
        )

        if (bool1 and bool2):
            loginf("No Problem")
        else:
            logging.warning("Coherency problem in Licchavi object ")
