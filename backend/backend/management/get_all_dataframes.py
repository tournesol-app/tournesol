from io import BytesIO, StringIO
from zipfile import ZipFile

from backend.models import Video, VideoRating, ExpertRating
from backend.models import VideoComment, VideoCommentMarker
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
