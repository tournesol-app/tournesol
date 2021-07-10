import torch
from copy import deepcopy
from time import time

from .losses import model_norm, round_loss, models_dist
from .losses import node_local_loss, predict
from .metrics import extract_grad, sp
from .data_utility import expand_tens, one_hot_vids
from .visualisation import disp_one_by_line
from .hyperparameters import get_defaults

"""
Machine Learning algorithm, used in "ml_train.py"

Organisation:
- ML model and decentralised structure are here
- Data is handled in "ml_train.py"
- some helpful small functions are in "utilities.py"

Notations:
- node = user : contributor
- vid = vID : video, video ID
- score : score of a video outputted by the algorithm, range?

- idx : index
- l_someting : list of someting
- arr : numpy array
- tens : torch tensor
- dic : dictionnary

Structure:
- Licchavi class is the structure designed to include
    a global model and one for each node
-- read Licchavi __init__ comments to better understand

USAGE:
- hardcode training hyperparameters in Licchavi __init__
- use get_licchavi() to get an empty Licchavi structure
- use Licchavi.set_allnodes() to populate nodes
- use Licchavi.train() to train the models
- use Licchavi.output_scores() to get the results

"""

def get_model(nb_vids, gpu=False):
    model = torch.zeros(nb_vids, requires_grad=True)
    if gpu:
        return model.cuda()
    return model

# nodes organisation
class Licchavi():
    ''' Training structure including local models and general one '''
    def __init__(self, nb_vids, vid_vidx, crit, gpu=False):
        ''' 
        nb_vids: number of different videos rated by at least one contributor 
                    for this criteria
        vid_vidx: dictionnary of {vID: idx}
        crit: comparison criteria learnt
        '''
        self.nb_params = nb_vids  # number of parameters of the model(= nb of videos)
        self.vid_vidx = vid_vidx # {video ID : video index (for that criteria)}
        self.gpu = gpu # boolean for gpu usage (not implemented yet)
        self.criteria = crit # criteria learnt by this Licchavi

        self.opt = torch.optim.SGD   # optimizer
        # defined in "hyperparameters.py"
        self.lr_node = 0    # local learning rate (local scores)
        self.lr_s = 0     # local learning rate for s parameter
        self.lr_gen = 0  # global learning rate (global scores)
        self.gen_freq = 0  # generalisation frequency (>=1)
        self.w0 = 0     # regularisation strength
        self.w = 0    # default weight for a node

        self.get_model = get_model # neural network to use
        self.general_model = self.get_model(nb_vids, gpu)
        self.init_model = deepcopy(self.general_model) # saved for metrics
        self.last_grad = None
        self.opt_gen = self.opt([self.general_model], lr=self.lr_gen)
        self.pow_gen = (1,1)  # choice of norms for Licchavi loss 
        self.pow_reg = (2,1)  # (internal power, external power)

        self.nb_nodes = 0
        self.nodes = {}

        # self.size = nb_params(self.general_model) / 10_000
        self.history = ([], [], [], [], [], [], []) # all metrics recording (not totally up to date)
  
    def set_params(self, **params):
        """ set training hyperparameters """
        #self.opt = params["opt"]
        self.lr_node = params["lr_node"]    # local learning rate (local scores)
        self.lr_s = params["lr_s"]    # local learning rate for s parameter
        self.lr_gen = params["lr_gen"]  # global learning rate (global scores)
        self.gen_freq = params["gen_freq"] # generalisation frequency (>=1)
        self.w0 = params["w0"]      # regularisation strength
        self.w = params["w"]    # default weight for a node

    # ------------ input and output --------------------
    def _get_default(self):
        ''' Returns: - (default s, default model, default age) '''
        model_plus = (  torch.ones(1, requires_grad=True), # s
                        self.get_model(self.nb_params, self.gpu), # model
                        0 #age
                        )
        return model_plus

    def _get_saved(self, loc_models_old, id, nb_new):
        ''' Returns saved parameters updated or default 
        
        loc_models_old: saved parameters in dictionnary of tuples
        id: id of node (user)
        nb_new: number of new videos (since save)

        Returns:
        - (s, model, age), updated or default
        '''
        triple = loc_models_old.get(id, self._get_default())
        if id in loc_models_old.keys():
            s, mod, age = triple
            mod = expand_tens(mod, nb_new)
            triple = (s, mod, age)
        return triple

    def set_allnodes(self, data_dic, user_ids, verb=1):
        ''' Puts data in Licchavi and create a model for each node 
        
        data_distrib: data distributed by ml_train.distribute_data() 
                       ie list of (vID1_batch, vID2_batch, rating_batch, 
                                                            single_vIDs_batch)
        users_id: list/array of users IDs in same order 
        '''
        nb = len(data_dic)
        self.nb_nodes = nb
        self.users = user_ids
        self.nodes = { id:  [   *data, # 0 to 4: vID1, vID2, r, vIDs, mask
                                *self._get_default(), # 5 to 7: s, model, age
                                None,  # 8: optimizer
                                self.w, # 9: weight
                            ] for id, data in zip(user_ids, data_dic.values())}
        for node in self.nodes.values():
            lrs = self.lr_s / len(node[0]) # FIXME
            node[8] = self.opt( [   {'params': node[6]},
                                    {'params': node[5], 'lr': lrs},
                                        ], lr=self.lr_node)
        if verb>=1:
            print("Total number of nodes : {}".format(self.nb_nodes))

    def load_and_update(self, data_dic, user_ids, fullpath, verb=1):
        ''' loads weights and expands them as required 

        data_dic: dictionnary {userID: ()}
        user_ids: list/array of user IDs
        '''
        self.criteria, dic_old, gen_model_old, loc_models_old = torch.load(fullpath)
        nb_new = self.nb_params - len(dic_old) # number of new videos
        self.general_model = expand_tens(gen_model_old, nb_new) # initialize scores for new videos
        self.opt_gen = self.opt([self.general_model], lr=self.lr_gen)
        self.users = user_ids
        nbn = len(user_ids)
        self.nb_nodes = nbn
        
        self.nodes = { id: [    *data, # 0 to 4: vID1, vID2, r, vIDs, mask
                                # 5 to 7: s, model, age
                                *self._get_saved(loc_models_old, id, nb_new), 
                                None, # 8: optimizer, defined below
                                self.w # 9: weight
                            ] for id, data in zip(user_ids, data_dic.values())}                   
        for node in self.nodes.values(): # set optimizers
            lrs = self.lr_s / len(node[0]) # FIXME
            node[8] = self.opt( [   {'params': node[6]}, 
                                    {'params': node[5], 'lr': lrs},
                                        ], lr=self.lr_node)
        if verb>=1:
            print("Total number of nodes : {}".format(self.nb_nodes))

    def output_scores(self):
        ''' Returns video scores both global and local
        
        Returns :   
        - (tensor of all vIDS , tensor of global video scores)
        - (list of tensor of local vIDs , list of tensors of local video scores)
        '''
        local_scores = []
        list_ids_batchs = []
        with torch.no_grad():
            glob_scores = self.general_model
            for node in self.nodes.values():
                input = one_hot_vids(self.vid_vidx, node[3])
                output = predict(input, node[6]) 
                local_scores.append(output)
                list_ids_batchs.append(node[3])
            vids_batch = list(self.vid_vidx.keys())
        return (vids_batch, glob_scores), (list_ids_batchs, local_scores)

    def save_models(self, fullpath):
        ''' saves age and global and local weights, detached (no gradients) '''
        local_data = {id:  (node[5],            # s
                            node[6].detach(),   # model
                            node[7]            # age
                        ) for id, node in self.nodes.items()}
        saved_data = (  self.criteria,
                        self.vid_vidx,
                        self.general_model.detach(), 
                        local_data
                        )
        torch.save(saved_data, fullpath)
    # --------- utility --------------
    def _all_nodes(self, key):
        ''' get a generator of one parameter for all nodes '''
        dic = {"userid": 0, "vid1": 1, "vid2": 2, "r": 3, "vids": 4, 
                "s": 5, "model": 6, "age": 7, "opt": 8, "age": 9}
        idx = dic[key]
        for node in self.nodes.values():
            yield node[idx]
    
    def stat_s(self):
        ''' print s stats '''
        l_s = [(round_loss(s, 2), id) for s, id in zip(self._all_nodes("s"), 
                                                        self.nodes.keys() )]
        tens = torch.tensor(l_s)
        disp_one_by_line(l_s)
        tens = tens[:,0]
        print("mean of s: ", round_loss(torch.mean(tens), 2))
        print("min and max of s: ", round_loss(torch.min(tens), 2), 
                                    round_loss(torch.max(tens), 2) )
        print("var of s: ", round_loss(torch.var(tens), 2))

    # ---------- methods for training ------------
    def _set_lr(self): # DOESNT UPDATE S LRs
        ''' sets learning rates of optimizers according to Licchavi settings '''
        for node in self.nodes.values(): 
            node[8].param_groups[0]['lr'] = self.lr_node # node optimizer
        self.opt_gen.param_groups[0]['lr'] = self.lr_gen

    def _zero_opt(self):
        ''' resets gradients of all models '''
        for node in self.nodes.values():
            node[8].zero_grad()  # node optimizer 
        self.opt_gen.zero_grad() # general optimizer

    def _update_hist(self, epoch, fit, gen, reg, verb=1):
        ''' updates history '''
        self.history[0].append(round_loss(fit))
        self.history[1].append(round_loss(gen))
        self.history[2].append(round_loss(reg))

        dist = models_dist(self.init_model, self.general_model, pow=(2,0.5)) 
        norm = model_norm(self.general_model, pow=(2,0.5))
        self.history[3].append(round_loss(dist, 1))
        self.history[4].append(round_loss(norm, 1))
        grad_gen = extract_grad(self.general_model)
        if epoch > 1: # no previous model for first epoch
            scal_grad = sp(self.last_grad, grad_gen)
            self.history[5].append(scal_grad)
        else:
            self.history[5].append(0) # default value for first epoch
        self.last_grad = deepcopy(extract_grad(self.general_model)) 
        grad_norm = sp(grad_gen, grad_gen)  # use sqrt ?
        self.history[6].append(grad_norm)

    def _old(self, years):
        ''' increments age of nodes (during training) '''
        for node in self.nodes.values():
            node[7] += years 

    def _counters(self, c_gen, c_fit):
        ''' updates internal training counters '''
        fit_step = (c_fit >= c_gen) 
        if fit_step:
            c_gen += self.gen_freq
        else:
            c_fit += 1 
        return fit_step, c_gen, c_fit

    def _do_step(self, fit_step):
        ''' step for appropriate optimizer(s) '''
        if fit_step:  # updating local or global alternatively
            for node in self.nodes.values(): 
                node[8].step() # node optimizer   
        else:
            self.opt_gen.step()  

    def _print_losses(self, tot, fit, gen, reg):
        ''' prints losses '''
        print("total loss : ", tot) 
        print("fitting : ", round_loss(fit, 2),
                ', generalisation : ', round_loss(gen, 2),
                ', regularisation : ', round_loss(reg, 2))

    def _rectify_s(self):
        ''' ensures that no s went under 0 '''
        limit = 0.1
        with torch.no_grad():
            for node in self.nodes.values():
                if node[5] < limit: # node[5] = s
                    node[5][0] = limit

    # ====================  TRAINING ================== 

    def train(self, nb_epochs=None, verb=1):   
        ''' training loop '''
        nb_epochs = 2 if nb_epochs is None else nb_epochs
        time_train = time()
        self._set_lr()

        # initialisation to avoid undefined variables at epoch 1
        loss, fit_loss, gen_loss, reg_loss = 0, 0, 0, 0
        c_fit, c_gen = 0, 0
        
        const = 10  # just for visualisation (remove later)
        fit_scale = const 
        gen_scale = const  # node weights are used in addition
        reg_scale = const * self.w0

        reg_loss = reg_scale * model_norm(self.general_model, self.pow_reg)  

        # training loop 
        nb_steps = self.gen_freq + 1
        for epoch in range(1, nb_epochs + 1):
            if verb>=1: print("\nepoch {}/{}".format(epoch, nb_epochs))
            time_ep = time()

            for step in range(1, nb_steps + 1):
                fit_step, c_gen, c_fit = self._counters(c_gen, c_fit)
                if verb >= 2: 
                    txt = "(fit)" if fit_step else "(gen)" 
                    print("step :", step, '/', nb_steps, txt)
                self._zero_opt() # resetting gradients

                #----------------    Licchavi loss  -------------------------
                 # only first 2 terms of loss updated
                if fit_step:
                    #self._rectify_s()  # to prevent s from diverging (bruteforce)
                    fit_loss, gen_loss = 0, 0
                    for node in self.nodes.values():  
                        fit_loss += node_local_loss(node[6],  # local model
                                                    node[5],  # s
                                                    node[0],  # id_batch1
                                                    node[1],  # id_batch2
                                                    node[2])  # r_batch
                        g = models_dist(node[6],            # local model
                                        self.general_model, # general model
                                        self.pow_gen,       # norm
                                        node[4]             # mask
                                        ) 
                        gen_loss +=  node[9] * g  # node weight  * generalisation term
                    fit_loss *= fit_scale
                    gen_loss *= gen_scale
                    loss = fit_loss + gen_loss 
                          
                # only last 2 terms of loss updated 
                else:        
                    gen_loss, reg_loss = 0, 0
                    for node in self.nodes.values():   
                        g = models_dist(node[6],            # local model
                                        self.general_model, # general model
                                        self.pow_gen,       # norm
                                        node[4]             # mask
                                        )
                        gen_loss += node[9] * g  # node weight * generalis term
                    reg_loss = model_norm(self.general_model, self.pow_reg) 
                    gen_loss *= gen_scale
                    reg_loss *= reg_scale        
                    loss = gen_loss + reg_loss

                if verb >= 2:
                    total_out = round_loss(fit_loss + gen_loss + reg_loss)
                    self._print_losses(total_out, fit_loss, gen_loss, reg_loss)           
                # Gradient descent 
                loss.backward() 
                self._do_step(fit_step)   

            self._update_hist(epoch, fit_loss, gen_loss, reg_loss, verb)
            self._old(1)  # aging all nodes of 1 epoch
            if verb>=1: print("epoch time :", round(time() - time_ep, 2)) 

        # ----------------- end of training -------------------------------  
        if verb>=0: print("training time :", round(time() - time_train, 2)) 
        return self.history # self.train() returns lists of metrics

    # ------------ to check for problems --------------------------
    def check(self):
        ''' perform some tests on internal parameters adequation '''
        # population check
        b1 =  (self.nb_nodes == len(self.nodes))
        # history check
        b2 = True
        for l in self.history:
            b2 = b2 and (len(l) == len(self.history[0]))
        if (b1 and b2):
            print("No Problem")
        else:
            print("Coherency problem in Licchavi object ")

def get_licchavi(nb_vids, dic, crit, gpu=False):
    ''' Returns a Licchavi (ml decentralized structure)

    nb_vids: number of different videos rated by at least one contributor 
                for this criteria
    dic: dictionnary of {vID: idx}
    crit: criteria of users rating

    Returns:
    - Licchavi object with initialized global model and no local ones
    '''
    licch = Licchavi(nb_vids, dic, crit, gpu=gpu)
    params = get_defaults() # defaults hyperparameters from "hyperparameters.py"
    licch.set_params(**params)
    return licch
    