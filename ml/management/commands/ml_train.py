
from os import EX_NOPERM
from tournesol.models.video import ComparisonCriteriaScore, ContributorRating
from tournesol.models.video import ContributorRatingCriteriaScore, VideoCriteriaScore
from django.core.management.base import BaseCommand, CommandError
from numpy.core.numeric import full

from tournesol.models import Comparison
from settings.settings import CRITERIAS

import os
import logging

from ml.licchavi import get_licchavi
from ml.handle_data import select_criteria, shape_data
from ml.handle_data import distribute_data, distribute_data_from_save
from ml.handle_data import format_out_loc, format_out_glob
from ml.experiments import run_experiment, licch_stats

"""
Machine Learning main python file

Organisation:
- main file is here
- Data is handled in "handle_data.py"
- ML model and decentralised structure are in "licchavi.py"

Notations:
- node = user : contributor
- vid = vID : video, video ID
- rating : rating provided by a contributor between 2 videos, in [0,100] or [-1,1]
- score : score of a video outputted by the algorithm, arround [-10, 10]
- glob, loc : global, local
- idx : index
- l_someting : list of someting
- arr : numpy array
- tens : torch tensor
- dic : dictionnary
- verb : verbosity level
- VARIABLE_NAME : global variable

Structure:
- fetch_data() provides data from the database
- ml_run() uses this data as input, trains via shape_train_predict()
     and returns video scores
- save_data() takes these scores and save them to the database
- these 3 are called by Django at the end of this file

USAGE:
- define global variables EPOCHS, CRITERIAS
- set RESUME to True if you want to use previously trained models 
-- EPOCHS: number of training epochs
-- CRITERIAS: list of str (there is one training for each criteria)
- call ml_run(fetch_data()) if you just want the scores in python

"""
# global variables
TOURNESOL_DEV = bool(int(os.environ.get("TOURNESOL_DEV", 0))) # dev mode

FOLDER_PATH = "ml/checkpoints/" 
FILENAME = "models_weights"
PATH = FOLDER_PATH + FILENAME
os.makedirs(FOLDER_PATH, exist_ok=True)
RESUME = False # wether to resume training or not

EPOCHS = 150

def fetch_data():
    """ Fetches the data from the Comparisons model

    Returns:
    - comparison_data: list of 
        [   contributor_id: int, video_id_1: int, video_id_2: int, 
            criteria: str, score: float, weight: float  ]
    """
    comparison_data = [
        [ccs.comparison.user_id, ccs.comparison.video_1_id, 
            ccs.comparison.video_2_id, ccs.criteria, ccs.score, ccs.weight]
        for ccs 
        in ComparisonCriteriaScore.objects.all().prefetch_related("comparison")]
    return comparison_data

def shape_train_predict(comparison_data, crit, epochs, resume, verb=2):
    ''' Trains models and returns video scores for one criteria

    comparison_data: output of fetch_data()
    criteria: str, rating criteria
    resume: bool, resume previous processing
    Returns :   
    - (tensor of all vIDS , tensor of global video scores)
    - (list of tensor of local vIDs , list of tensors of local video scores)
    - list of users IDs in same order as second output
    '''
    one_crit = select_criteria(comparison_data, crit)
    full_data = shape_data(one_crit)
    fullpath = PATH + '_' + crit
    if resume:
        nodes_dic, users_ids, vid_vidx = distribute_data_from_save( full_data, 
                                                                    crit, 
                                                                    fullpath)
        licch = get_licchavi(len(vid_vidx), vid_vidx, crit) 
        licch.load_and_update(nodes_dic, users_ids, fullpath, verb)
    else:
        nodes_dic, users_ids, vid_vidx = distribute_data(full_data)
        licch = get_licchavi(len(vid_vidx), vid_vidx, crit)
        licch.set_allnodes(nodes_dic, users_ids, verb)
    h = licch.train(epochs, verb=verb) 
    glob, loc = licch.output_scores()
    licch.save_models(fullpath)
    if TOURNESOL_DEV:
        licch_stats(licch)
    return glob, loc, users_ids

def ml_run(comparison_data, epochs, criterias, resume, verb=2):
    """ Runs the ml algorithm for all CRITERIAS (global variable)
    
    comparison_data: output of fetch_data()

    Returns:
    - video_scores: list of [video_id: int, criteria_name: str, 
                                score: float, uncertainty: float]
    - contributor_rating_scores: list of 
    [   contributor_id: int, video_id: int, criteria_name: str, 
        score: float, uncertainty: float]
    """ # FIXME: not better to regroup contributors in same list or smthg ?
    glob_scores, loc_scores = [], []
    for criteria in criterias:
        logging.info("PROCESSING " + criteria)
        glob, loc, users_ids = shape_train_predict( comparison_data, 
                                                    criteria, 
                                                    epochs,
                                                    resume, 
                                                    verb) 
        # putting in required shape for output
        out_glob = format_out_glob(glob, criteria) 
        out_loc = format_out_loc(loc, users_ids, criteria) 
        glob_scores += out_glob
        loc_scores += out_loc
    return glob_scores, loc_scores

def save_data(video_scores, contributor_rating_scores):
    """
    Saves in the scores for Videos and ContributorRatings
    """
    VideoCriteriaScore.objects.all().delete()
    VideoCriteriaScore.objects.bulk_create([
        VideoCriteriaScore(
            video_id=video_id,
            criteria=criteria,
            score=score,
            uncertainty=uncertainty,
        )
        for video_id, criteria, score, uncertainty in video_scores
    ])

    rating_ids = {
        (contributor_id, video_id): rating_id
        for rating_id, contributor_id, video_id 
        in ContributorRating.objects.all().values_list( "id", 
                                                        "user_id", 
                                                        "video_id")
    }
    ratings_to_create = set(
        (contributor_id, video_id)
        for contributor_id, video_id, _, _, _
        in contributor_rating_scores
        if (contributor_id, video_id) not in rating_ids
    )
    created_ratings = ContributorRating.objects.bulk_create([
        ContributorRating(
            video_id=video_id,
            user_id=contributor_id,
            is_public=False,
        )
        for contributor_id, video_id in ratings_to_create 
    ])
    rating_ids.update({
        (rating.user_id, rating.video_id): rating.id
        for rating in created_ratings
    })
    ContributorRatingCriteriaScore.objects.all().delete()
    ContributorRatingCriteriaScore.objects.bulk_create([
        ContributorRatingCriteriaScore(
            contributor_rating_id=rating_ids[(contributor_id, video_id)],
            criteria=criteria,
            score=score,
            uncertainty=uncertainty,
        )
        for contributor_id, video_id, criteria, score, uncertainty 
        in contributor_rating_scores
    ])

    
class Command(BaseCommand):
    help = 'Runs the ml'
    def handle(self, *args, **options):
        comparison_data = fetch_data()
        if TOURNESOL_DEV: 
            run_experiment(comparison_data)
        else: 
            glob_scores, loc_scores = ml_run(   comparison_data, 
                                                EPOCHS, 
                                                CRITERIAS, 
                                                RESUME,
                                                verb=-1)
            save_data(glob_scores, loc_scores)
