from io import BytesIO, StringIO
from zipfile import ZipFile
import pandas as pd
from backend.models import Video, VideoRating, ExpertRating, HistoricalExpertRating
from backend.models import VideoComment, VideoCommentMarker, UserInformation, \
    VideoRatingPrivacy
from backend.rating_fields import VIDEO_FIELDS
from django.contrib.auth.models import User as DjangoUser
from django_pandas.io import read_frame


def get_user_data(username):
    """Get user's personal data."""
    dfs = {}

    df = read_frame(Video.objects.all(), fieldnames=['id', 'video_id'] + VIDEO_FIELDS)
    dfs['all_video_ratings'] = df

    df = read_frame(VideoRating.objects.filter(user__user__username=username).all())
    dfs['my_video_scores'] = df

    df = read_frame(ExpertRating.objects.filter(user__user__username=username).all())
    dfs['my_expert_ratings'] = df

    df = read_frame(VideoComment.objects.filter(user__user__username=username).all())
    dfs['my_video_comments'] = df

    df = read_frame(VideoCommentMarker.objects.filter(user__user__username=username).all(),
                    fieldnames=['id', 'user', 'comment__id', 'user', 'which'])
    dfs['my_video_comment_markers'] = df

    return dfs


def get_database_as_pd():
    """Get database tables as pandas DataFrames."""
    result_df = {}

    df = read_frame(
        Video.objects.all(),
        fieldnames=[
            'id',
            'video_id',
            'name',
            'duration',
            'language',
            'publication_date',
            'views',
            'uploader'] +
        VIDEO_FIELDS)
    result_df['videos'] = df

    df = read_frame(VideoRating.objects.all())
    result_df['video_ratings'] = df

    df = read_frame(ExpertRating.objects.all())
    result_df['expert_rating'] = df

    df = read_frame(
        DjangoUser.objects.all(),
        fieldnames=[
            'id',
            'last_login',
            'is_superuser',
            'username',
            'first_name',
            'last_name',
            'is_staff',
            'is_active',
            'date_joined',
            'email',
            'userpreferences__id'] + [
            f"userpreferences__{x}" for x in VIDEO_FIELDS])
    result_df['users'] = df

    df = read_frame(VideoComment.objects.all())
    result_df['video_comment'] = df

    df = read_frame(VideoCommentMarker.objects.all(), fieldnames=[
                    'id', 'user', 'comment__id', 'user', 'which'])
    result_df['video_comment_marker'] = df

    return result_df


def get_public_append_only_database_as_pd():
    """Get the public append-only database."""
    result_df = {}

    # all history for ratings, with both videos rated publicly
    qs = HistoricalExpertRating.objects.all()
    for v in '12':
        qs = VideoRatingPrivacy._annotate_privacy(qs, prefix=f'video_{v}__videoratingprivacy',
                                                  output_prefix=f"_v{v}")
    qs = qs.filter(_v1_is_public=True, _v2_is_public=True)

    result_df['comparison_database'] = read_frame(qs, fieldnames=[
            'id', 'duration_ms', 'datetime_lastedit', 'datetime_add',
            *VIDEO_FIELDS,
            *[x + '_weight' for x in VIDEO_FIELDS],
            'user__user__username',
            'video_1__video_id', 'video_2__video_id',
            'history_id', 'history_date', 'history_change_reason', 'history_type'
            ])

    # getting all user data (without demo accounts)
    qs = UserInformation.objects.all().filter(is_demo=False)

    # adding _is_certified field
    qs = UserInformation._annotate_is_certified(qs)

    # a horrible hack to make django-pandas work with annotations
    # see https://github.com/chrisdev/django-pandas/blob/master/django_pandas/io.py
    # TODO: fix it
    import django
    django.db.models.fields.FieldDoesNotExist = django.core.exceptions.FieldDoesNotExist

    #Even if 'show my profile' is false, export 'username'.
    # If 'show my profile' is true, export 'First name',
    # 'Last name', 'Title', 'Bio',
    # If 'show online presence' is true, export 'Website',
    # 'Linkedin', 'Youtube', 'Google scholar', 'Orcid', 'Researchgate', 'Twitter'.
    # Do NOT share demographic data.

    # only username
    fields_basic = UserInformation.BASIC_FIELDS + ['_is_certified']
    qs1 = qs.filter(show_my_profile=False)
    df1 = read_frame(qs1, fieldnames=fields_basic)

    # username and info
    fields_profile = UserInformation.PROFILE_FIELDS
    qs2 = qs.filter(show_my_profile=True, show_online_presence=False)
    df2 = read_frame(qs2, fieldnames=fields_basic + fields_profile)

    # username, info and online fields
    fields_online = UserInformation.ONLINE_FIELDS
    qs3 = qs.filter(show_my_profile=True, show_online_presence=True)
    df3 = read_frame(qs3, fieldnames=fields_basic + fields_profile + fields_online)

    # all contributors
    df = pd.concat([df1, df2, df3], axis=0, ignore_index=True)

    result_df['contributors_public'] = df

    return result_df


def save_dfs_get_zip(dfs_fcn=get_database_as_pd):
    """Save dataframes to csv and get a zip file."""
    dfs = dfs_fcn()

    # creating the archive
    f = BytesIO()
    zipObj = ZipFile(f, "w")

    # saving dataframes as csv
    for name, df in dfs.items():
        csv_f = StringIO()
        fullname = name + ".csv"
        df.to_csv(csv_f, index=False)
        csv_f.seek(0)
        zipObj.writestr(fullname, csv_f.read())

    zipObj.close()
    f.seek(0)

    return f
