import torch

"""
Losses used in "licchavi.py"

Main file is "ml_train.py"
"""

def predict(input, tens):
    ''' Predicts score according to a model

    Args:
        tens (float tensor): tensor = model
        input (bool tensor: tensor one-hot encoding video

    Returns: 
        float tensor: score of the video according to the model
    '''
    return torch.matmul(input.float(), tens)

# losses (used in licchavi.py)
def fbbt(t,r):
    ''' fbbt loss function 

    Args:
        t (float tensor): s * (ya - yb).
        r (float tensor): rating given by user.

    Returns:
        float tensor: empirical loss for one comparison.
    '''
    return torch.log(abs(torch.sinh(t)/t)) + r * t + torch.log(torch.tensor(2))

def hfbbt(t,r):
    ''' Approximated fbbt loss function 

    Args:
        t (float tensor): s * (ya - yb).
        r (float tensor): rating given by user.

    Returns:
        float tensor: empirical loss for one comparison.
    '''
    if abs(t) <= 0.01:
        return t**2 / 6 + r *t + torch.log(torch.tensor(2))
    elif abs(t) < 10:
        return torch.log(2 * torch.sinh(t) / t) + r * t
    else:
        return abs(t) - torch.log(abs(t)) + r * t

def fit_loss(s, ya, yb, r):  
    ''' Loss for one comparison 
    
    Args:
        s (float tensor): s parameter.
        ya (float tensor): predicted score of video a.
        yb (float tensor): predicted score of video b.
        r (float tensor): rating given by user between a and b.

    Returns:
         float tensor: empirical loss for this comparison.
    '''
    loss = hfbbt(s * (ya - yb), r)   
    return loss

def s_loss(s):
    ''' Second term of local loss (for one node) 
    
    Args:
        s (float tensor): s parameter.
    
    Returns:
        float tensor: second half of local loss
    '''
    return (0.5 * s**2 - torch.log(s))

def node_local_loss(model, s, a_batch, b_batch, r_batch):
    ''' fitting loss for one node, includes s_loss 
    
    Args:
        model (float tensor): node local model.
        s (float tensor): s parameter.
        a_batch (bool 2D tensor): first videos compared by user.
        b_batch (bool 2D tensor): second videos compared by user.
        r_batch (float tensor): rating provided by user.

    Returns:
        float: node local loss.
    '''
    ya_batch = predict(a_batch, model)
    yb_batch = predict(b_batch, model)
    loss = 0 
    for ya,yb,r in zip(ya_batch, yb_batch, r_batch):
        loss += fit_loss(s, ya, yb, r)
    return loss + s_loss(s) 

def models_dist(model1, model2, pow=(1,1), mask=None):  
    ''' distance between 2 models (l1 by default)

    Args:
        model1 (float tensor): scoring model
        model2 (float tensor): scoring model
        pow (float, float): (internal power, external power)
        mask (bool tensor): subspace in which to compute distance

    Returns:
        float: distance between the 2 models
    '''
    q, p = pow
    if mask is None:
        mask = [torch.ones_like(param) for param in [model1]]
    dist = sum(
                (((theta - rho) * coef)**q).abs().sum() for theta, rho, coef 
                                        in zip([model1], [model2], mask)
                )**p
    return dist

def model_norm(model, pow=(2,1)): 
    ''' norm of a model (l2 squared by default)

    Args:
        model (float tensor): scoring model
        pow (float, float): (internal power, external power)

    Returns: 
        float: norm of the model
    '''
    q, p = pow
    norm = sum((param**q).abs().sum() for param in [model])**p
    return norm

def round_loss(tens, dec=0): 
    ''' from an input scalar tensor or int/float returns rounded int/float '''
    if type(tens)==int or type(tens)==float:
        return round(tens, dec)
    else:
        return round(tens.item(), dec)
