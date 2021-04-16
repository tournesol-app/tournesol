from backend.models import ExpertRating
from backend.rating_fields import VIDEO_FIELDS, MAX_VALUE
from django.db.models import F, Value, FloatField, Func, CharField
from django.db.models.functions import Power


def disagreements_for_user(user_preferences, top=20,
                           threshold_mse_normed=0.12):
    """Get top disagreements between the model and the representative."""

    qs = ExpertRating.objects.all()
    qs = qs.filter(user=user_preferences)
    qs = qs.filter(video_1__videorating__user=user_preferences,
                   video_2__videorating__user=user_preferences)

    # adding video scores
    annotations = {}
    for vid in [1, 2]:
        for f in VIDEO_FIELDS:
            annotations[f'video_{vid}_score_{f}'] = F(f'video_{vid}__videorating__{f}')
    qs = qs.annotate(**annotations)

    # computing model pairwise rating
    annotations = {}
    for f in VIDEO_FIELDS:
        # 1.0 / (1 + Math.exp(modelV1[feature] - modelV2[feature]))
        one = Value(1., output_field=FloatField())

        def exp(x):
            return Func(x, function='EXP')

        delta = F(f'video_1_score_{f}') - F(f'video_2_score_{f}')
        delta = one + exp(delta)
        delta = one / delta

        annotations[f'model_{f}_01'] = delta
    qs = qs.annotate(**annotations)

    # scaling up/down
    annotations = {}
    for f in VIDEO_FIELDS:
        annotations[f'model_{f}'] = Value(MAX_VALUE, output_field=FloatField())\
                                           * F(f'model_{f}_01')
        annotations[f'{f}_01'] = F(f) / Value(MAX_VALUE, output_field=FloatField())
    qs = qs.annotate(**annotations)

    # computing disagreement and thresholding...
    annotations = {}
    for f in VIDEO_FIELDS:
        annotations[f'mse_{f}_01'] = Power(F(f'model_{f}_01') - F(f'{f}_01'),
                                           Value(2.0, output_field=FloatField()))
    qs = qs.annotate(**annotations)

    # sorting over all fields and returning top 20
    qs_fs = []
    tot_count = 0
    for f in VIDEO_FIELDS:
        qs_f = qs.filter(**{f'mse_{f}_01__gte': threshold_mse_normed})
        tot_count += qs_f.count()
        qs_f = qs_f.order_by(f'-mse_{f}_01')
        qs_f = qs_f[:top]
        qs_f = qs_f.annotate(mse_01=F(f'mse_{f}_01'),
                             feature=Value(f, output_field=CharField()),
                             model_score=F(f'model_{f}'),
                             rating_score=F(f))
        qs_fs.append(list(qs_f))

    qs_f_all = [x for qs in qs_fs for x in qs]
    qs_f_all = sorted(qs_f_all, key=lambda x: -x.mse_01)
    # return qs_f_all
    qs_f_all = qs_f_all[:top]

    for item in qs_f_all:
        item.video_1__video_id = item.video_1.video_id
        item.video_2__video_id = item.video_2.video_id

    return {'count': tot_count,
            'results': qs_f_all}
