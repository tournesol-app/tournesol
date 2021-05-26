from io import BytesIO, StringIO
import zipfile

from django_pandas.io import read_frame
import numpy as np
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from django.db.utils import IntegrityError

from backend.api_v2.video_ratings import get_score_annotation
from backend.constants import fields as constants
from backend.models import DjangoUser, UserPreferences, EmailDomain, \
    UserInformation, VerifiableEmail, Video, ExpertRating, VideoRatingPrivacy
from backend.models import VIDEO_FIELDS
from helpers import random_alphanumeric, create_test_video, login, logout, \
    TIME_WAIT, get, open_tournesol


def create_toy_data(django_db_blocker, driver,
                    n_users=10, n_videos=10,
                    n_ratings=10):
    """Create a random database."""

    with django_db_blocker.unblock():
        users = [DjangoUser.objects.create_user(
                username=random_alphanumeric(), is_active=True)
                for u in range(n_users)]

        video_ids = [create_test_video() for v in range(n_videos)]

    # creating user preferences and user informations
    login(driver)
    logout(driver)

    # creating email domains
    status_to_domain = {EmailDomain.STATUS_ACCEPTED: "@accepted.com",
                        EmailDomain.STATUS_REJECTED: "@rejected.com",
                        EmailDomain.STATUS_PENDING: "@pending.com"}
    with django_db_blocker.unblock():
        for status, domain in status_to_domain.items():
            EmailDomain.objects.create(domain=domain, status=status)

    # obtaining user information/user preferences
    with django_db_blocker.unblock():
        ups = [UserPreferences.objects.get(user__username=u.username)
               for u in users]
        uis = [UserInformation.objects.get(user__username=u.username)
               for u in users]

    # setting show_my_profile and show_online_presence to random values
    with django_db_blocker.unblock():
        for ui in uis:
            ui.show_my_profile = np.random.rand() > 0.5
            ui.show_online_presence = np.random.rand() > 0.5

    # filling in user informations
    with django_db_blocker.unblock():
        for ui in uis:
            # filling online presence
            for field in UserInformation.ONLINE_FIELDS:
                domain = UserInformation._domain_startswith.get(field, "mydomain.com")
                setattr(ui, field, f"https://{domain}/{random_alphanumeric()}")

            # filling personal data
            for field in UserInformation.PROFILE_FIELDS:
                setattr(ui, field, random_alphanumeric())

            # filling in protected attributes
            protected_map = {
                    'birth_year': 1990,
                    'gender': 'Male',
                    'nationality': 'Swiss',
                    'residence': 'Switzerland',
                    'race': 'Latino or Hispanic',
                    'political_affiliation': 'Centrist',
                    'religion': 'Atheist',
                    'degree_of_political_engagement': 'Light',
                    'moral_philosophy': 'Utilitatian'
            }

            for key, val in protected_map.items():
                setattr(ui, key, val)

            ui.save()

    # assigning random emails
    with django_db_blocker.unblock():
        for ui in uis:
            domain = np.random.choice(list(status_to_domain.values()))
            email = f"{random_alphanumeric()}{domain}"
            verified = np.random.rand() > 0.8
            VerifiableEmail.objects.create(email=email, user=ui, is_verified=verified)

    # creating random ratings
    with django_db_blocker.unblock():
        for up in ups:

            for _ in range(n_ratings):
                fields = {}

                for f in VIDEO_FIELDS:
                    fields[f] = np.random.rand() * 100
                    fields[f + "_weight"] = np.random.rand() + 1

                vid1 = np.random.choice(video_ids)
                vid2 = np.random.choice(video_ids)

                v1 = Video.objects.get(video_id=vid1)
                v2 = Video.objects.get(video_id=vid2)

                try:
                    ExpertRating.objects.create(user=up, video_1=v1, video_2=v2, **fields)
                except IntegrityError:
                    print("Duplicate random comparison (OK)")
                    pass

    # assigning random privacy settings
    with django_db_blocker.unblock():
        for up in ups:
            for video_id in video_ids:
                if np.random.rand() > 0.5:
                    continue

                public = np.random.rand() > 0.8

                VideoRatingPrivacy.objects.create(
                        video=Video.objects.get(video_id=video_id),
                        user=up, is_public=public)


def test_download_privacy_public_database(driver, django_db_blocker):
    """Test that public database is a zip archive, and it only contains public info."""

    create_toy_data(django_db_blocker=django_db_blocker,
                    driver=driver, n_users=30, n_videos=100,
                    n_ratings=30)

    open_tournesol(driver)

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, "id_public_database_download")))

    link = driver.find_element_by_id('id_public_database_download').get_attribute('href')

    data = get(link)
    assert data.ok
    assert data.content
    assert data.headers['content-type'] == 'application/zip'

    # with open('data.zip', 'wb') as f:
    #     f.write(data.content)

    # reading dataframes
    zip_file = BytesIO(data.content)
    dfs = {}
    with zipfile.ZipFile(zip_file, 'r') as zf:
        for fileinfo in zf.infolist():
            content = zf.read(fileinfo).decode('ascii')
            df = pd.read_csv(StringIO(content))
            dfs[fileinfo.filename] = df

    # print(data.content)

    assert set(dfs.keys()) == set(
        ['comparison_database.csv', 'contributors_public.csv',
         'all_video_scores.csv']
    ), f"Wrong files in archive: {dfs.keys()}"

    # checking comparisons privacy
    df = dfs['comparison_database.csv']
    for _, row in df.iterrows():
        username = row['user__user__username']
        vid1 = row['video_1__video_id']
        vid2 = row['video_2__video_id']

        # both videos must be rated publicly!
        with django_db_blocker.unblock():
            for vid in [vid1, vid2]:
                qs = Video.objects.filter(video_id=vid)
                assert qs.count() == 1, (qs, qs.count())
                up = UserPreferences.objects.get(user__username=username)
                qs = VideoRatingPrivacy._annotate_privacy(qs, prefix="videoratingprivacy",
                                                          field_user=up)
                assert qs.count() == 1, (qs, qs.count())
                assert qs.get()._is_public, qs.values()

        print("Check for", username, vid1, vid2, "successful")

    # checking user information privacy
    df = dfs['contributors_public.csv']
    for _, row in df.iterrows():
        username = row['user__username']

        # checking certification status
        with django_db_blocker.unblock():
            qs = UserInformation.objects.filter(user__username=username)
            assert qs.count() == 1, qs
            qs = UserInformation._annotate_is_certified(qs)
            assert qs.count() == 1, qs
            ui = qs.get()
        assert ui._is_certified == row['_is_certified'], (dict(row), ui)

        # checking show_my_profile
        if not ui.show_my_profile:
            for f in UserInformation.PROFILE_FIELDS:
                assert pd.isna(row[f]), row[f]

        # checking online presence
        if not ui.show_online_presence or not ui.show_my_profile:
            for f in UserInformation.ONLINE_FIELDS:
                assert pd.isna(row[f]), row[f]

        # checking that protected fields are not included
        for f in UserInformation.PROTECTED_FIELDS:
            assert f not in row, (f, row)

        print("Check for", username, "successful")


def test_integrity_of_all_video_scores(driver, django_db_blocker):
    """
    Test the integrity of the public file all_video_scores.csv.

    The file is considered correct if:
        - it contains all videos of the database
        - it contains only the expected columns
        - it contains a correct calculation of the Tournesol score
    """
    create_toy_data(django_db_blocker=django_db_blocker, driver=driver,
                    n_users=2, n_videos=4,
                    n_ratings=2)

    open_tournesol(driver)

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, "id_public_database_download")))

    link = driver.find_element_by_id('id_public_database_download').get_attribute('href')

    data = get(link)
    assert data.ok
    assert data.content
    assert data.headers['content-type'] == 'application/zip'

    zip_file = BytesIO(data.content)
    dfs = {}
    with zipfile.ZipFile(zip_file, 'r') as zf:
        for fileinfo in zf.infolist():
            content = zf.read(fileinfo).decode('ascii')
            df = pd.read_csv(StringIO(content))
            dfs[fileinfo.filename] = df

    # the file must be in the public zip archive
    assert "all_video_scores.csv" in dfs.keys()

    df = dfs['all_video_scores.csv']
    default_features = [constants['DEFAULT_PREFS_VAL'] for _ in VIDEO_FIELDS]

    # the file must contain only expected columns
    assert set(df.columns) == set(["id", "video_id", "score"] + VIDEO_FIELDS)

    with django_db_blocker.unblock():
        # good ol' hack to make django-pandas work with annotations
        import django
        django.db.models.fields.FieldDoesNotExist = django.core.exceptions.FieldDoesNotExist

        # the file must contain all video in the database, with their correct
        # Tournesol score and value for each criterion
        video_df = read_frame(
            Video.objects.all().annotate(score=get_score_annotation(default_features)),
            fieldnames=['id', 'video_id', 'score'] + VIDEO_FIELDS
        )

        assert df.equals(video_df)
