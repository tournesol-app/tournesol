from torch import optim

"""
To set hyperparameters for Licchavi object in "licchavi.py"

Main file is "ml_train.py"
"""

def get_defaults():
    """ defaults training parameters """
    defaults = {
                "w0": 1,  # float >= 0, regularisation parameter
                "w": 1,   # float >= 0, harmonisation parameter
                "lr_gen": 0.001,     # float > 0, learning rate of global model
                "lr_node": 0.01,    # float > 0, learning rate of local models
                "lr_s" : 0.0001,   # float > 0, learning rate of s parameters
                "gen_freq": 1, # int >= 1, number of global steps 
                               #                 for 1 local step
                
                #"opt": optim.SGD,    # any torch otpimizer
                #"nb_epochs": 100 # int >= 1, number of training epochs
                }
    return defaults
