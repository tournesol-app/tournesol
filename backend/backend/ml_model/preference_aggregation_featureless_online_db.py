import gin
import numpy as np
from backend.models import VideoRating, Video, ExpertRating, UserPreferences, UserInformation
from backend.rating_fields import VIDEO_FIELDS, MAX_VALUE
from django.db.models import Q, F, Count


def select_adjacent_videos(video_pks, filt, hops=1, limit_other_videos=20, videos_hard_limit=100,
                           rating_hard_limit=100):
    """Get ratings that are related to the video in k hops."""
    queue = []  # format: (hops, video)

    visited = set()
    ratings = set()

    for pk in video_pks:
        queue.append((0, pk))

    while queue:
        curr_hops, item = queue[0]
        queue = queue[1:]

        if item in visited:
            continue

        if len(visited) > videos_hard_limit:
            break

        visited.add(item)

        if curr_hops < hops:

            curr_res = set()
            related_1 = ExpertRating.objects.filter(filt & Q(video_1__id=item)).values(
                'video_2__id', 'id')
            for item_next in related_1:
                curr_res.add(item_next['video_2__id'])
                ratings.add(item_next['id'])

                if len(ratings) > rating_hard_limit:
                    break

            related_2 = ExpertRating.objects.filter(filt & Q(video_2__id=item)).values(
                'video_1__id', 'id')
            for item_next in related_2:
                curr_res.add(item_next['video_1__id'])
                ratings.add(item_next['id'])

                if len(ratings) > rating_hard_limit:
                    break

            # adding children
            for item_next in curr_res.difference(visited):
                queue.append((curr_hops + 1, item_next))

    if len(visited) > 2 + limit_other_videos:
        other_videos_lst = list(visited.difference(video_pks))
        visited = video_pks + list(
            np.random.choice(other_videos_lst, size=limit_other_videos, replace=False))

    ratings = ExpertRating.objects.filter(pk__in=ratings).filter(
        Q(video_1__pk__in=visited) & Q(video_2__pk__in=visited)).values_list('id')
    ratings = [x[0] for x in ratings]

    return visited, ratings


def get_from_list(qs, field, values):
    """Bulk get from database."""
    qs = qs.filter(**{f'{field}__in': values}).annotate(__f=F(field))
    qs_dct = {obj.__f: obj for obj in qs}
    lst = [qs_dct.get(val, None) for val in values]
    return lst


def sample_certified_users_with_video(video_pks, max_other_users=1, feature_nonan=None,
                                      always_include_username=None):
    """Get a list of usernames which have most ratings on a particular list of videos."""
    qs = UserPreferences.objects.all()

    # removing myself to get more others (will add later)
    if always_include_username is not None:
        qs = qs.exclude(user__username=always_include_username)

    # filter for expert ratings
    expertrating_filter = Q(pk__in=[])
    for video_pk in video_pks:
        expertrating_filter = expertrating_filter | Q(expertrating__video_1__pk=video_pk)
        expertrating_filter = expertrating_filter | Q(expertrating__video_2__pk=video_pk)

    # exclude ratings with a NaN value
    if feature_nonan is not None:
        expertrating_filter = expertrating_filter & Q(
            **{'expertrating__' + feature_nonan + '__isnull': False})

    qs = UserInformation._annotate_is_certified(qs, prefix='user__userinformation__')
    qs = qs.filter(_is_certified=True)
    qs = qs.annotate(_rating_count=Count('expertrating',
                                         filter=expertrating_filter,
                                         distinct=True
                                         ))

    filter_rating_exists = Q(pk__in=[])
    for video_pk in video_pks:
        qs = qs.annotate(
            **{
                f'_v_{video_pk}_nonnull':
                    Count('videorating',
                          filter=Q(videorating__video__pk=video_pk,
                                   **{'videorating__' + feature_nonan + '__isnull': False}))
            })
        filter_rating_exists = filter_rating_exists | Q(**{f'_v_{video_pk}_nonnull__gt': 0})

    # at least one score must be present for any of the videos
    qs = qs.filter(filter_rating_exists)

    # expert ratings must exist
    qs = qs.filter(_rating_count__gt=0)

    # selecting by top ratings
    qs = qs.order_by('-_rating_count')[:max_other_users]

    lst = qs.values_list('user__username')
    usernames_set = set([x[0] for x in lst])

    if always_include_username is not None:
        usernames_set.add(always_include_username)

    return usernames_set


@gin.configurable
class OnlineRatingUpdateContext():
    """Returns model tensor and the minibatch for a particular rating."""

    def __init__(self, expert_rating, feature, user_set_value=None):
        assert feature in VIDEO_FIELDS, (feature, VIDEO_FIELDS)
        assert isinstance(expert_rating, ExpertRating), expert_rating

        # rating to change
        self.expert_rating = expert_rating
        self.feature = feature

        # destructuring the rating
        self.video1 = self.expert_rating.video_1
        self.video2 = self.expert_rating.video_2
        self.my_username = self.expert_rating.user.user.username

        # list of me + people who rated the video most
        self.usernames = list(sample_certified_users_with_video(
            [self.video1.pk, self.video2.pk],
            always_include_username=self.my_username, feature_nonan=self.feature))

        # updater to get hyperparameters
        from .preference_aggregation_featureless_online import FeaturelessOnlineUpdater
        online = FeaturelessOnlineUpdater()

        # selecting videos and ratings
        self.videos, self.ratings = select_adjacent_videos(
            [self.video1.id, self.video2.id],
            Q(user__user__username__in=self.usernames,
              **{self.feature + '__isnull': False}))
        self.videos = list(self.videos)
        self.ratings = list(self.ratings)

        # must have the rating-to-change in the set
        if self.expert_rating.id not in self.ratings:
            self.ratings.append(self.expert_rating.id)

        # obtaining objects
        self.videos_selected = get_from_list(Video.objects.all(), 'pk', self.videos)
        self.ratings_selected = get_from_list(ExpertRating.objects.all(), 'pk', self.ratings)

        # print(self.videos_selected, self.ratings_selected)

        # obtaining video scores
        self.scores_for_usernames = {
            username:
                get_from_list(VideoRating.objects.filter(user__user__username=username),
                              'video__pk',
                              self.videos)
            for username in self.usernames
        }

        # obtaining ratings
        self.ratings_for_usernames = {
            username:
                ExpertRating.objects.filter(pk__in=self.ratings).filter(
                    user__user__username=username)
            for username in self.usernames
        }

        # map video PK -> internal ID (in model tensor)
        self.video_id_idx_reverse = {idx: i for i, idx in enumerate(self.videos)}

        # default score value
        self.score_default = online.hypers['default_score_value']

        # internal IDs for the videos
        self.obj1 = self.video_id_idx_reverse[self.video1.id]
        self.obj2 = self.video_id_idx_reverse[self.video2.id]

        # tensor with scores
        self.model_tensor = None

        # ratings in minibatch form
        self.minibatch_construct = None
        self.mb_np = None

        # ID in the minibatch to change
        self.idx_set = None

        # obtaining data from db...
        self.fill_model_tensor()
        self.fill_minibatch()

    def write_updates_to_db(self, new_model_tensor):
        # writing individual scores
        def update_user_from_tensor(obj_i, username):
            score = new_model_tensor[self.usernames.index(username), obj_i, 0]
            VideoRating.objects.filter(user__user__username=username,
                                       video__pk=self.videos[obj_i]). \
                update(**{self.feature: score})

        for username in self.usernames:
            update_user_from_tensor(self.obj1, username)
            update_user_from_tensor(self.obj2, username)

        # writing aggregated scores
        def update_agg_from_tensor(obj_i):
            score = new_model_tensor[-1, obj_i, 0]
            Video.objects.filter(pk=self.videos[obj_i]). \
                update(**{self.feature: score})

        # writing global scores
        update_agg_from_tensor(self.obj1)
        update_agg_from_tensor(self.obj2)

    def fill_model_tensor(self):
        """Create the tensor with TS scores and representative scores."""
        # shape: (len(usernames) + 1, len(videos), 1==1 feature)
        self.model_tensor = np.full(fill_value=self.score_default,
                                    shape=(len(self.usernames) + 1, len(self.videos), 1),
                                    dtype=np.float32)

        # filling in common model scores
        for i, video in enumerate(self.videos_selected):
            self.model_tensor[-1, i, 0] = getattr(video, self.feature)

        # filling in user representative scores
        for i, username in enumerate(self.usernames):
            for score in self.scores_for_usernames[username]:
                if score is None:
                    continue
                video_internal_id = self.video_id_idx_reverse[score.video.id]
                self.model_tensor[i, video_internal_id, 0] = getattr(score, self.feature)

    def fill_minibatch(self):
        """Fill minibatch data with ratings of selected users."""
        self.minibatch_construct = {
            'experts_rating': [],
            'objects_rating_v1': [],
            'objects_rating_v2': [],
            'cmp': [],
            'weights': [],
            'experts_all': [],
            'objects_all': [],
            'num_ratings_all': [],
            'objects_common_to_1': []
        }

        # fit loss
        minibatch_rating_current_item = 0
        minibatch_match = []
        for i, username in enumerate(self.usernames):
            for rating in self.ratings_for_usernames[username]:
                v1_internal = self.video_id_idx_reverse[rating.video_1.id]
                v2_internal = self.video_id_idx_reverse[rating.video_2.id]

                self.minibatch_construct['experts_rating'].append(i)
                self.minibatch_construct['objects_rating_v1'].append(v1_internal)
                self.minibatch_construct['objects_rating_v2'].append(v2_internal)

                z = getattr(rating, self.feature)
                if z is None:
                    z = MAX_VALUE / 2.

                self.minibatch_construct['cmp'].append(
                    [2 * (z / MAX_VALUE - 0.5)])
                self.minibatch_construct['weights'].append(
                    [getattr(rating, self.feature + "_weight")])

                if username == self.my_username and v1_internal == self.obj1 \
                        and v2_internal == self.obj2:
                    minibatch_match.append(minibatch_rating_current_item)

                minibatch_rating_current_item += 1

        assert len(minibatch_match) == 1, minibatch_match
        self.idx_set = minibatch_match[0]

        # regularization: common to expert
        for i, username in enumerate(self.usernames):
            for j, video in enumerate(self.videos_selected):
                self.minibatch_construct['experts_all'].append(i)
                self.minibatch_construct['objects_all'].append(j)
                self.minibatch_construct['num_ratings_all'].append(video.get_rating_n_ratings())

        # regularization: common to 1
        for i, video in enumerate(self.videos_selected):
            self.minibatch_construct['objects_common_to_1'].append(i)

        self.mb_np = {x: np.array(y) for x, y in self.minibatch_construct.items()}
