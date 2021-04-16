"""Cache for online update contexts (minibatch+model tensor)."""

from threading import current_thread
from time import time

from backend.ml_model.preference_aggregation_featureless_online_db import OnlineRatingUpdateContext
from backend.models import ExpertRating
from django_react.settings import load_gin_config
from copy import deepcopy

# format: thread id -> (expert rating PK, field) -> (created_time, OnlineRatingUpdateContext)
_cache = {}
MAX_CACHE_PER_THREAD = 1000


def current_thread_id():
    """ID of the current Django thread."""
    return current_thread().ident


def current_cache():
    """Cache for the current thread."""
    tid = current_thread_id()
    if tid not in _cache:
        _cache[tid] = {}
    return _cache[tid]


def invalidate(rating_pk, field):
    """Remove an element from the cache."""
    cache = current_cache()
    key = (rating_pk, field)
    if key in cache:
        del cache[key]


def cached_class_instance(rating_pk, field, timeout_sec=100):
    """Get a cached instance or create one"""
    cache = current_cache()
    current_time = time()

    # key to search for in the cache
    key = (rating_pk, field)

    # invalidating old caches...
    # TODO: replace with a faster implementation
    for existing_key in deepcopy(list(cache.keys())):
        if current_time - cache[existing_key][0] >= timeout_sec:
            del cache[existing_key]

    # need to add a new element, and there are too many already...
    if key not in cache and len(cache) >= MAX_CACHE_PER_THREAD:
        raise ValueError("Too many elements in cache, please wait and try again...")

    # creating an item if it doesn't exist or if it's too old
    if key not in cache or current_time - cache[key][0] >= timeout_sec:
        load_gin_config('backend/ml_model/config/featureless_config.gin')
        cache[key] = (current_time, OnlineRatingUpdateContext(
            expert_rating=ExpertRating.objects.get(pk=rating_pk),
            feature=field))

    # returning the object
    return {'cache': cache[key][1],
            'cache_created': cache[key][0]}
