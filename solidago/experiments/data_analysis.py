from solidago.pipeline.inputs import TournesolDataset
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy

data = TournesolDataset.download()

criteria = {
    "reliability": "Reliable and not misleading",
    "importance": "Important and actionable",
    "engaging": "Engaging and thought-provoking",
    "pedagogy": "Clear and pedagogical",
    "layman_friendly": "Layman-friendly",
    "diversity_inclusion": "Diversity and inclusion",
    "backfire_risk": "Resilience to backfiring risks",
    "better_habits": "Encourages better habits",
    "entertaining_relaxing": "Entertaining and relaxing"
}
entities = set(data.comparisons.entity_a) | set(data.comparisons.entity_b)
user_ids = set(data.comparisons.user_id)

def add_comparison_analysis_columns(comparisons):
    def is_first_comparison(comparisons):
        registered = { e: set() for e in entities }
        entity_a_firsts, entity_b_firsts = list(), list()
        for _, r in comparisons.iterrows():
            entity_a_first, entity_b_first = False, False
            if r.criteria == "largely_recommended" and r.user_id not in registered[r.entity_a]:
                registered[r.entity_a].add(r.user_id)
                entity_a_first = True
            if r.criteria == "largely_recommended" and r.user_id not in registered[r.entity_b]:
                registered[r.entity_b].add(r.user_id)            
                entity_b_first = True
            entity_a_firsts.append(entity_a_first)
            entity_b_firsts.append(entity_b_first)
        return entity_a_firsts, entity_b_firsts
        
    entity_a_firsts, entity_b_firsts = is_first_comparison(comparisons)
    comparisons = comparisons.assign(entity_a_first=entity_a_firsts)
    comparisons = comparisons.assign(entity_b_first=entity_b_firsts)
    
    def score_of_first_comparison(comparisons):
        first_comparison_score = list()
        for _, r in comparisons.iterrows():
            if r.entity_a_first and (not r.entity_b_first):
                first_comparison_score.append(r.score)
            elif (not r.entity_a_first) and r.entity_b_first:
                first_comparison_score.append(- r.score)
            else:
                first_comparison_score.append(np.nan)
        return first_comparison_score
    
    comparisons = comparisons.assign(first_comparison_score=score_of_first_comparison(comparisons))
    
    def has_others(comparisons):
        with_others = dict()
        for _, r in comparisons[comparisons.criteria != "largely_recommended"].iterrows():
            if r.user_id not in with_others:
                with_others[r.user_id] = dict()
            if r.entity_a not in with_others[r.user_id]:
                with_others[r.user_id][r.entity_a] = set()
            with_others[r.user_id][r.entity_a].add(r.entity_b)
        has_others = list()
        for _, r in comparisons.iterrows():
            has_others.append(
                r.user_id in with_others
                and r.entity_a in with_others[r.user_id]
                and r.entity_b in with_others[r.user_id][r.entity_a]
            )
        return has_others
        
    comparisons = comparisons.assign(has_others=has_others(comparisons))
    
    def is_trusted(comparisons):
        return [data.users.loc[r.user_id, "trust_score"] >= 0.8 for _, r in comparisons.iterrows()]
    
    comparisons = comparisons.assign(is_trusted=is_trusted(comparisons))
    
    return comparisons

c = add_comparison_analysis_columns(data.comparisons)

def add_user_analysis_columns(users, comparisons):
    def n_comparisons(users, comparisons):
        return [
            len(comparisons[comparisons.user_id == user_id])
            for user_id, _ in data.users.iterrows()
        ]
    users = users.assign(n_comparisons=n_comparisons(users, comparisons))
    users = users.assign(
        n_main_comparisons=n_comparisons(
            users, 
            comparisons[comparisons.criteria == "largely_recommneded"]
        )
    )
    return users
    
u = add_user_analysis_columns(data.users, data.comparisons)

def add_score_analysis_columns():
    def _unsquash(scores):
        for _, row in scores[scores.score == 100.00].iterrows():
            row.score = 99.99
        for _, row in scores[scores.score == -100.00].iterrows():
            row.score = -99.99
        return scores.score / np.sqrt(100.0**2 - scores.score)
    
    data.collective_scores = data.collective_scores.assign(unsquashed=_unsquash(data.collective_scores.scores))
    data.individual_scores = data.individual_scores.assign(unsquashed=_unsquash(data.individual_scores.scores))

def confidence_interval(scores, confidence=0.95):
    mean = scores.mean()
    z_deviation = np.sqrt(2) * scipy.special.erfinv(confidence)
    deviation = z_deviation * np.sqrt( scores.var() / len(scores) )
    return mean - deviation, mean + deviation

def plot_criteria(comparisons, figsize=(2, 3)):
    fig, axs = plt.subplots(3, 3, figsize=figsize)
    for n_plot, ax in enumerate(axs.flat):
        criterion = list(criteria.keys())[n_plot]
        cc = comparisons[comparisons.criteria == criterion]
        ax.hist(cc.score, bins=21)
        ax.set_title(criteria[criterion])

def n_extreme_values(scores, n_std_dev):
    mean = scores.mean()
    std_dev = np.sqrt(scores.var())
    return len(scores[np.abs(scores - mean) > n_std_dev * std_dev])
    
def plot(comparison_scores, colors=("g", "y", "r"), labels=None):
    if labels is None:
        plt.hist(comparison_scores, 21, density=True, histtype='bar', color=colors)
    else:
        plt.hist(comparison_scores, 21, density=True, histtype='bar', color=colors, label=labels)
