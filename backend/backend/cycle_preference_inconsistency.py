import networkx as nx
import numpy as np
from backend.models import ExpertRating, Video
from backend.rating_fields import VIDEO_FIELDS, MAX_VALUE
from django.db.models import F, Value, FloatField, Func, Q


def get_edges_list(queryset, feature, print_ties=False,
                   threshold_delta=0.05):
    """Get list of edges for a username for a feature.
    Args:
        queryset (django queryset): qs with ratings
        feature (str): one of VIDEO_FEATURES
        print_ties (bool): if true, print vids with equal scores

    Returns:
        Array with entries [parent, child, {'weight': score}]
    """
    ratings_u_f = queryset

    # idA -> idB if idA is rated higher on feature f
    edges = []
    for r in ratings_u_f:
        value = getattr(r, feature)
        if value is None:
            continue
        dist_from_50 = np.abs((MAX_VALUE / 2) - value)
        videos = [r.video_1.video_id, r.video_2.video_id]
        if value < MAX_VALUE * (0.5 - threshold_delta):  # A is better than B
            edges.append(videos + [{'weight': dist_from_50}])
        elif value > MAX_VALUE * (0.5 + threshold_delta):  # B is better than A
            edges.append(videos[::-1] + [{'weight': dist_from_50}])
        elif print_ties:
            print("tie %s %s" % tuple(videos))

    return edges


def graph_from_edges(edges):
    """Return a graph given a list of edges."""
    G = nx.DiGraph()
    if not edges:
        return G
    G.add_nodes_from(np.unique(np.array(edges)[:, :2].flatten()))
    G.add_edges_from(np.array(edges))
    return G


def inconsistencies_for_queryset(user, queryset=None):
    """Get inconsistencies (cycles) for a particular username."""

    if queryset is None:
        queryset = ExpertRating.objects.filter(user=user)

    results = []
    for f in VIDEO_FIELDS:
        edges = get_edges_list(queryset, f)
        G = graph_from_edges(edges)
        for c in nx.simple_cycles(G):
            c = c + [c[0]]
            ratings = list(zip(c[:-1], c[1:]))
            cmp = []
            for r in ratings:
                v1 = Video.objects.get(video_id=r[0])
                v2 = Video.objects.get(video_id=r[1])
                try:
                    rating = ExpertRating.objects.get(
                        video_1=v1, video_2=v2, user=user)
                except ExpertRating.DoesNotExist:
                    try:
                        rating = ExpertRating.objects.get(
                            video_1=v2, video_2=v1, user=user)
                    except ExpertRating.DoesNotExist:
                        raise Exception("Rating does not exist")

                cmp.append({'videoA': rating.video_1.video_id,
                            'videoB': rating.video_2.video_id,
                            'score': getattr(rating, f),
                            'id': rating.id})
            r = {'feature': f,
                 'videos': c,
                 'comparisons': cmp}
            results.append(r)
    return results


def get_edges_list_db(queryset, feature,
                      threshold_delta=0.05):
    """Get list of edges for a username for a feature using queries.
    Args:
        queryset (django queryset): qs with ratings
        feature (str): one of VIDEO_FEATURES

    Returns:
        Array with entries [parent, child, {'weight': score}]
    """

    qs = queryset

    # don't need null values
    qs = qs.filter(**{f'{feature}__isnull': False})
    qs = qs.annotate(_feature=F(feature) / Value(MAX_VALUE, output_field=FloatField()))

    # computing edge weight
    qs = qs.annotate(_dist_from_middle=Func(
        Value(0.5, output_field=FloatField())
        - F('_feature'),
        function='ABS'))

    # only care about sufficiently strong edges
    qs = qs.filter(_dist_from_middle__gt=threshold_delta)

    # edges with first video better
    qs1 = qs.filter(_feature__lt=0.5)
    qs1val = qs1.values_list('video_1__id', 'video_2__id', '_dist_from_middle')

    qs2 = qs.filter(_feature__gt=0.5)
    qs2val = qs2.values_list('video_2__id', 'video_1__id', '_dist_from_middle')

    edges = {(x[0], x[1]): x[2] for z in [qs1val, qs2val] for x in z}

    return edges


def get_cycles_weights_3(edges):
    """Return a list of cycles of length 3 in a directed graph.

    Input: map (from, to) -> edge weight

    See https://github.com/tournesol-app/tournesol/issues/288.
    """
    nodes = ({x[0] for x in edges.keys()}).union({x[1] for x in edges.keys()})

    # undirected edges
    undirected_edges = {}
    for (a, b), w in edges.items():
        undirected_edges[(a, b)] = w
        undirected_edges[(b, a)] = -w

    # map node -> list ofnodes s.t. there is an edge a->b or b->a and key(a) < key(b)
    undirected_edges_to_greater = {n: [] for n in nodes}

    # filling in the map
    for a, b in edges.keys():
        if a < b:
            undirected_edges_to_greater[a].append(b)
        else:  # a > b
            undirected_edges_to_greater[b].append(a)

    cycles_3 = []
    weights_3 = []

    # lexicographically first node2
    for node1 in sorted(nodes):
        # greater values
        # list of undirected edge destinations which are lexic. greater
        for node2 in undirected_edges_to_greater[node1]:
            for node3 in undirected_edges_to_greater[node2]:
                if (node1, node3) in undirected_edges:
                    weights = (undirected_edges[(node1, node2)],
                               # weight > 0 if a better than b according to feature
                               undirected_edges[(node2, node3)],
                               # weight < 0 if a worse than b according to feature
                               undirected_edges[(node3, node1)],)

                    # if all signs are equal
                    if len(set(np.sign(weights))) == 1:
                        cycles_3.append((node1, node2, node3))
                        weights_3.append(weights)
    return cycles_3, weights_3


def inconsistencies_3_for_queryset(user, queryset=None,
                                   top_inc=10):
    """Get 3-inconsistencies (cycles of length 3) for a particular username.

    See https://github.com/tournesol-app/tournesol/issues/288.
    """

    if queryset is None:
        queryset = ExpertRating.objects.filter(user=user)

    # inconsistency objects
    results = []

    for f in VIDEO_FIELDS:
        # computing inconsistencies...
        edges = get_edges_list_db(queryset, f)
        cycles_3, weights_3 = get_cycles_weights_3(edges)

        if not cycles_3:
            continue

        # selecting ones with maximal weight
        cycles_3 = np.array(cycles_3)
        avg_weight = np.array(weights_3).mean(axis=1)
        avg_abs_weight = np.abs(avg_weight)
        idx_order_top = np.argsort(avg_abs_weight)[::-1][:top_inc]

        # selecting top cycles
        top_cycles = cycles_3[idx_order_top]
        top_weights_abs = avg_abs_weight[idx_order_top]
        top_weights = avg_weight[idx_order_top]

        # obtaining a map pk -> video ID
        video_ids_set = list(np.unique(cycles_3.flatten()))
        all_videos = Video.objects.filter(pk__in=video_ids_set).values('id', 'video_id')
        id_to_video_id = {}
        for v in all_videos:
            id_to_video_id[v['id']] = v['video_id']

        # list of ratings to obtain the scores
        all_ratings = ExpertRating.objects.filter(Q(user=user) &
                                                  (Q(video_1__id__in=video_ids_set) |
                                                   Q(video_2__id__in=video_ids_set))
                                                  ).values('video_1__id',
                                                           'video_2__id',
                                                           f, 'id')
        rating_vids_to_score_and_id = {}
        for r in all_ratings:
            rating_vids_to_score_and_id[(r['video_1__id'],
                                         r['video_2__id'])] = (r[f], r['id'])

        for i, (v1, v2, v3) in enumerate(top_cycles):
            # comparisons
            cmp = []

            # reversing the order if weight is negative
            if top_weights[i] < 0:
                (v1, v2, v3) = (v3, v2, v1)

            # list of rating pairs
            pairs = [(v1, v2), (v2, v3), (v3, v1)]

            # youtube video IDs
            video_ids = [id_to_video_id[pk] for pk in (v1, v2, v3)]

            # adding pairs to comparison array...
            for va, vb in pairs:
                # obtaining rating in correct order...

                if (va, vb) in rating_vids_to_score_and_id:
                    rev = False
                    score, rid = rating_vids_to_score_and_id[(va, vb)]
                else:
                    rev = True
                    score, rid = rating_vids_to_score_and_id[(vb, va)]

                cmp.append({
                    'videoA': id_to_video_id[va],
                    'videoB': id_to_video_id[vb],
                    'score': score if not rev else MAX_VALUE - score,
                    'id': rid,
                    'reverse': rev
                })

            r = {'feature': f,
                 'videos': video_ids + [video_ids[0]],
                 'comparisons': cmp,
                 'weight': top_weights_abs[i]}
            results.append(r)

    results = sorted(results, key=lambda x: x['weight'], reverse=True)

    return results
