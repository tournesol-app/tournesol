import torch
from copy import deepcopy
from time import time
import logging
from logging import info as loginf
import gin

from .losses import (round_loss, predict, loss_fit_s_gen, loss_gen_reg)
from .metrics import (
    get_uncertainty_loc, get_uncertainty_glob, update_hist,
    check_equilibrium_glob, check_equilibrium_loc)
from .data_utility import expand_tens, one_hot_vids
from .nodes import Node

"""
Machine Learning algorithm, used in "core.py"

Organisation:
- ML model and decentralised structure are here
- Main file is "ml_train.py"

Structure:
- Licchavi class is the structure designed to include
    a global model and one for each node
-- read Licchavi __init__ comments to better understand

USAGE:
- hardcode training hyperparameters in "hyperparameters.py"
- use get_licchavi() to get an empty Licchavi structure
- use Licchavi.set_allnodes() to populate nodes
- use Licchavi.train() to train the models
- use Licchavi.output_scores() to get the results
"""


def get_model(nb_vids, device='cpu'):
    custom = 0
    if custom:
        model = torch.ones(nb_vids, device=device) * custom
        model.requires_grad = True
        return model
    return torch.zeros(nb_vids, requires_grad=True, device=device)


def get_s(device='cpu'):
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
            metrics=None,
            lr_node=None,
            lr_s=None,
            lr_gen=None,
            gen_freq=None,
            nu=None,
            w0=None,
            w=None
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
        self.lr_node = lr_node    # local learning rate (local scores)
        self.lr_s = lr_s     # local learning rate for s parameter
        self.lr_gen = lr_gen  # global learning rate (global scores)
        self.gen_freq = gen_freq  # generalisation frequency (>=1)
        self.nu = nu  # importance of s_loss term
        self.w0 = w0     # regularisation strength
        self.w = w   # default weight for a node

        self.get_model = get_model  # neural network to use
        self.global_model = self.get_model(nb_vids, device)
        self.init_model = deepcopy(self.global_model)  # saved for metrics
        self.last_grad = None
        self.opt_gen = self.opt([self.global_model], lr=self.lr_gen)

        self.nb_nodes = 0
        self.nodes = {}
        self.history = {metric: [] for metric in metrics}

        self.users = []  # users IDs

    def _show(self, msg, level):
        """ Utility for handling logging messages

        msg (str): info message
        level (float): minimum level of verbosity to show -msg
        """
        if self.verb >= level:
            loginf(msg)

    # ------------ input and output --------------------
    def _get_default(self):
        """ Returns: - (default s, default model, default age) """
        model_plus = (
            get_s(self.device),  # s
            self.get_model(self.nb_vids, self.device),  # model
            0  # age
        )
        return model_plus

    def _get_saved(self, loc_models_old, id, nb_new):
        """ Returns saved parameters updated or default

        loc_models_old (dictionnary): saved parameters in dictionnary of tuples
                                        {user ID: (s, model, age)}
        id (int): id of node (user)
        nb_new (int): number of new videos (since save)

        Returns:
            (s, model, age), updated or default
        """
        if id in loc_models_old:
            s, mod, age = loc_models_old[id]
            mod = expand_tens(mod, nb_new, self.device)
            triple = (s, mod, age)
        else:
            triple = self._get_default()
        return triple

    def set_allnodes(self, data_dic, users_ids):
        """ Puts data in Licchavi and create a model for each node

        data_dic (dictionnary): {userID: (vID1_batch, vID2_batch,
                                            rating_batch, single_vIDs, masks)}
        users_ids (int array): users IDs
        """
        nb = len(data_dic)
        self.nb_nodes = nb
        self.users = users_ids
        self.nodes = {id: Node(
            *data,
            *self._get_default(),
            self.w,
            self.lr_node,
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
        self.opt_gen = self.opt([self.global_model], lr=self.lr_gen)
        self.users = user_ids
        nbn = len(user_ids)
        self.nb_nodes = nbn
        self.nodes = {
            id: Node(
                *data,
                *self._get_saved(loc_models_old, id, nb_new),
                self.w,
                self.lr_node,
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
                input = one_hot_vids(self.vid_vidx, node.vids, self.device)
                output = predict(input, node.model)
                loc_scores.append(output)
                list_vids_batchs.append(node.vids)
            vids_batch = list(self.vid_vidx.keys())

        return (vids_batch, glob_scores), (list_vids_batchs, loc_scores)

    def save_models(self, fullpath):
        """ Saves age and global and local weights, detached (no gradients) """
        loginf('Saving models')
        local_data = {id:  (node.s,            # s
                            node.model.detach(),   # model
                            node.age            # age
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

    # ---------- methods for training ------------
    def _set_lr(self):
        """ Sets learning rates of optimizers """
        for node in self.nodes.values():
            node.opt.param_groups[0]['lr'] = self.lr_node  # node optimizer
            # FIXME update lr_s (not useful currently)
        self.opt_gen.param_groups[0]['lr'] = self.lr_gen

    @gin.configurable
    def _lr_schedule(
            self, epoch,
            # configured with gin in "hyperparameters.gin"
            decay_rush, decay_fine,
            precision, epsilon,
            min_lr_fine, lr_rush_duration):
        """ Changes learning rates in a (hopefully) smart way

        epoch (int): current epoch
        verb (int): verbosity level

        Returns:
            (bool): True for an early stopping
        """

        # phase 1  : rush (high lr to increase l2 norm fast)
        if epoch <= lr_rush_duration:
            self.lr_gen *= decay_rush
            self.lr_node *= decay_rush
        # phase 2 : fine tuning (low lr), we monitor equilibrium for early stop
        elif epoch % 2 == 0:
            if self.lr_node >= min_lr_fine / decay_fine:
                self.lr_gen *= decay_fine
                self.lr_node *= decay_fine
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
            node.opt.zero_grad(set_to_none=True)  # node optimizer
        self.opt_gen.zero_grad(set_to_none=True)  # general optimizer

    def _old(self, years):
        """ Increments age of nodes (during training) """
        for node in self.nodes.values():
            node.age += years

    def _do_step(self, fit_step):
        """ Makes step for appropriate optimizer(s) """
        if fit_step:  # updating local or global alternatively
            for node in self.nodes.values():
                node.opt.step()  # node optimizer
        else:
            self.opt_gen.step()

    def _regul_s(self):
        """ regulate s parameters """
        for node in self.nodes.values():
            if node.s <= 0:
                with torch.no_grad():
                    node.s[0] = 0.0001
                    logging.warning('Regulating negative s')

    def _print_losses(self, tot, fit, s, gen, reg):
        """ Prints losses into log info """
        fit, s = round_loss(fit, 2), round_loss(s, 2)
        gen, reg = round_loss(gen, 2), round_loss(reg, 2)

        loginf(f'total loss : {tot}\nfitting : {fit}, '
               f's : {s}, generalisation : {gen}, regularisation : {reg}')

    # ====================  TRAINING ==================
    def _do_epoch(self, epoch, nb_epochs):
        """ Trains for one epoch

        epoch (int): current epoch
        nb_epochs (int): (maximum) number of epochs
        """
        self._show("epoch {}/{}".format(epoch, nb_epochs), 1)
        time_ep = time()

        nb_steps = self.gen_freq + 1  # one fitting step
        for step in range(1, nb_steps + 1):
            fit_step = (step == 1)  # fitting on first step only

            self._show(f'step : {step}/{nb_steps} '
                       f'{"(fit)" if fit_step else "(gen)"}', 2)
            self._zero_opt()  # resetting gradients

            # ----------------    Licchavi loss  -------------------------
            # only first 3 terms of loss updated
            if fit_step:
                fit_loss, s_loss, gen_loss = loss_fit_s_gen(self)
                loss = fit_loss + s_loss + gen_loss
            # only last 2 terms of loss updated
            else:
                gen_loss, reg_loss = loss_gen_reg(self)
                loss = gen_loss + reg_loss

            if self.verb >= 2:
                total_loss = round_loss(fit_loss + s_loss
                                        + gen_loss + reg_loss)
                self._print_losses(total_loss, fit_loss, s_loss,
                                   gen_loss, reg_loss)
            # Gradient descent
            loss.backward()
            self._do_step(fit_step)

        update_hist(self, (fit_loss, s_loss, gen_loss, reg_loss, epoch))
        self._old(1)  # aging all nodes of 1 epoch
        self._show(f'epoch time :{round(time() - time_ep, 2)}', 1.5)

    def train(self, nb_epochs=1, compute_uncertainty=False):
        """ training loop

        nb_epochs (int): (maximum) number of training epochs
        compute_uncertainty (bool): wether to compute uncertainty
            at the end or not (takes time)

        Returns:
            (float list list, float tensor): uncertainty of local scores
                                            (None, None) if not computed
        """
        loginf('STARTING TRAINING')
        time_train = time()

        # training loop
        for epoch in range(1, nb_epochs + 1):
            early_stop = self._lr_schedule(epoch)
            if early_stop:
                break  # don't do this epoch nor any other
            self._set_lr()
            self._regul_s()
            self._do_epoch(epoch, nb_epochs)

        loginf('END OF TRAINING\n'
               f'Training time: {round(time() - time_train, 2)}')

        if compute_uncertainty:  # FIXME make separate method ?
            time_uncert = time()
            uncert_loc = get_uncertainty_loc(self)
            uncert_glob = get_uncertainty_glob(self)
            loginf(f'Uncertainty time: {time() - time_uncert}')
            return uncert_glob, uncert_loc  # self.train() returns uncertainty
        return None, None  # if uncertainty not computed

    # ------------ to check for problems --------------------------
    def check(self):
        """ Performs some tests on internal parameters adequation """
        # population check
        b1 = (self.nb_nodes == len(self.nodes))
        # history check
        reference = list(self.history.values())[0]
        b2 = all([len(v) == len(reference) for v in self.history.values()])

        if (b1 and b2):
            loginf("No Problem")
        else:
            logging.warning("Coherency problem in Licchavi object ")
