import datetime
import re
import uuid
from functools import partial

import numpy as np
import pytest
from backend.constants import youtubeVideoIdRegex
from backend.models import Video, UserPreferences, ExpertRating, VideoReports, \
    VideoComment, VideoRating, VideoCommentMarker, UserInformation, VerifiableEmail, EmailDomain,\
    VideoRatingPrivacy
from backend.rating_fields import VIDEO_FIELDS, VIDEO_REPORT_FIELDS
from backend.tests.helpers import get_singleton, get_date_ago
from django.contrib.auth.models import User as DjangoUser
from backend.rating_fields import MAX_VALUE as MAX_RATING
from rest_framework.test import APIClient
import json


@pytest.fixture(scope='session')
def TEST_USERNAME():
    return str(uuid.uuid1())


@pytest.fixture(scope='session')
def TEST_PASSWORD():
    return str(uuid.uuid1())


@pytest.fixture()
def client(TEST_USERNAME, TEST_PASSWORD):
    """Get an API connection."""
    client = APIClient()  # enforce_csrf_checks=True)
    client.login(username=TEST_USERNAME, password=TEST_PASSWORD)
    yield client
    client.logout()


def create_users(name, password):
    """Create test user."""
    dj_user = DjangoUser.objects.create_user(username=name, password=password,
                                             email=f"{name}@example.com",
                                             is_active=True)
    prefs = UserPreferences.objects.create(user=dj_user)
    return dj_user, prefs


@pytest.fixture(scope='session')
def django_db_setup(
        django_db_setup,
        django_db_blocker,
        TEST_USERNAME,
        TEST_PASSWORD):
    """Set up the database: create a user in the system with user preferences."""
    with django_db_blocker.unblock():
        create_users(name=TEST_USERNAME, password=TEST_PASSWORD)


def set_user_preferences(current_user_preferences, prefs):
    """Set test user's preferences."""
    assert len(VIDEO_FIELDS) == len(prefs)
    for i, f in enumerate(VIDEO_FIELDS):
        setattr(current_user_preferences, f, prefs[i])
    current_user_preferences.save()


def set_video_scores(video, scores):
    """Set scores for a video."""
    assert len(VIDEO_FIELDS) == len(scores)
    for i, f in enumerate(VIDEO_FIELDS):
        setattr(video, f, scores[i])
    video.save()


@pytest.fixture
def current_user(TEST_USERNAME):
    """Get test Django User."""
    return DjangoUser.objects.get(username=TEST_USERNAME)


@pytest.fixture
def current_user_preferences(current_user):
    """Get current user preferences."""
    return UserPreferences.objects.get(user=current_user)


def with_redirect(method):
    """Follow redirects properly for patch."""

    def inner(*args, **kwargs):
        """Assuming first arg is the url."""
        args = list(args)
        ok = False
        while not ok:
            result = method(*args, **kwargs)
            if result.status_code != 302:
                return result
            else:
                args[0] = result.url

    return inner


def query_string(dct):
    """Form a querystring."""
    qs = '&'.join([f"{k}={v}" for k, v in dct.items()])
    print(qs)
    return qs


@pytest.mark.django_db
class TestAPI(object):
    """Run API tests."""

    def get_videos_req(self, client, **kwargs):
        """Get videos with given params."""
        r = client.get('/api/v2/videos/search_tournesol/', data=kwargs)
        assert r.status_code == 200
        try:
            return r.json()['results']
        except ValueError as e:
            for x in dir(r):
                print(x)
            print("Cannot decode", r.content)
            raise e

    def test_root(self, client):
        r = client.get('/api/v2/')
        assert r.status_code == 200

    def test_videos(self, client, current_user_preferences):
        """Test that can create and show videos."""

        get_videos_req = partial(self.get_videos_req, client=client)

        # removing everything from the database
        Video.objects.all().delete()

        # hopefully, the test runs fast enough...
        date_10_days_ago = get_date_ago(days=10)
        date_100_days_ago = get_date_ago(days=100)

        v1_params = dict(video_id="test1",
                         name="test_name",
                         description="test_video_description",
                         duration=datetime.timedelta(minutes=10),
                         publication_date=date_10_days_ago,
                         language='fr',
                         views=100500,
                         uploader="FamousPerson")

        v2_params = {'video_id': 'test2'}

        # creating one video using python
        Video.objects.create(**v1_params)

        # and another using API
        r = client.post('/api/v2/videos/', data=v2_params)
        assert r.status_code == 201

        # can't add twice!
        r = client.post('/api/v2/videos/', data=v2_params)
        assert r.status_code == 400

        # should have 2 objects now
        assert len(Video.objects.all()) == 2

        v1 = Video.objects.get(video_id="test1")
        v2 = Video.objects.get(video_id="test2")
        v2.name = "test_name2"
        v2.language = "en"
        v2.duration = datetime.timedelta(seconds=120)
        v2.publication_date = date_100_days_ago
        v2.views = 50
        v2.uploader = 'NotSoFamousPerson'
        v2.save()

        # checking that manual video is there
        for key, val in v1_params.items():
            val1 = getattr(v1, key)
            assert val1 == val, f"{val1}, {val}"

        # checking that API video is there
        for key, val in v2_params.items():
            val1 = getattr(v2, key)
            if key == 'duration':
                val1 = val1.total_seconds()
            if key == 'publication_date':
                val1 = val1.strftime('%Y-%m-%d')
            assert val1 == val, f"{val1}, {val}"

        # setting all values for preferences to 0
        # this leads to no videos shown
        # as their score becomes 0
        # unless we search with words...
        set_user_preferences(current_user_preferences=current_user_preferences,
                             prefs=[0] * len(VIDEO_FIELDS))

        # both videos have non-zero score because of the search string
        assert len(get_videos_req(search="test")) == 2

        # but without the search string, all scores are 0
        assert len(get_videos_req()) == 0
        assert len(get_videos_req(video_id="test1")) == 0
        assert len(get_videos_req(video_id="test2")) == 0

        # setting the score (otherwise, the API doesn't return the video)
        # setting my user preferences
        set_user_preferences(current_user_preferences=current_user_preferences,
                             prefs=range(1, len(VIDEO_FIELDS) + 1))

        # still 0 because we didn't set video scores
        assert len(get_videos_req()) == 0
        assert len(get_videos_req(video_id="test1")) == 0
        assert len(get_videos_req(video_id="test2")) == 0

        set_video_scores(v1, np.arange(len(VIDEO_FIELDS)) + 1 + 10)

        # now have 1
        assert len(get_videos_req()) == 1
        assert len(get_videos_req(video_id="test1")) == 1
        assert len(get_videos_req(video_id="test2")) == 0

        set_video_scores(v2, np.arange(len(VIDEO_FIELDS)) + 1 + 20)

        # now have 2
        assert len(get_videos_req()) == 2
        assert len(get_videos_req(video_id="test1")) == 1
        assert len(get_videos_req(video_id="test2")) == 1

        # now let's test filtering: number of videos
        for n in [1, 2, 3, 4]:
            assert len(get_videos_req(limit=n)) == min(2, n)

        # now let's test language
        assert get_singleton(get_videos_req(language="fr"))[
                   'video_id'] == "test1"
        assert get_singleton(get_videos_req(language="en"))[
                   'video_id'] == "test2"
        assert not get_videos_req(language="blah-blah")

        # testing duration
        assert get_singleton(
            get_videos_req(
                duration_gte=3 * 60))['video_id'] == 'test1'
        assert get_singleton(
            get_videos_req(
                duration_lte=9 * 60))['video_id'] == 'test2'
        assert not get_videos_req(duration_gte=9 * 60, duration_lte=1 * 60)

        # testing number of views
        assert get_singleton(get_videos_req(views_gte=1000))[
                   'video_id'] == 'test1'
        assert get_singleton(get_videos_req(views_lte=1000))[
                   'video_id'] == 'test2'
        assert not get_videos_req(views_gte=10, views_lte=9)

        # testing date (time ago)
        assert get_singleton(get_videos_req(days_ago_lte=30))[
                   'video_id'] == 'test1'
        assert len(get_videos_req(days_ago_lte=365)) == 2

        # now checking the scores
        v1r = get_singleton(get_videos_req(video_id="test1"))
        v2r = get_singleton(get_videos_req(video_id="test2"))

        # checking that API score_info matches the video
        for v, vr in zip([v1, v2], [v1r, v2r]):
            for f in VIDEO_FIELDS:
                assert getattr(v, f) == vr[f]
            assert vr['score_search_term'] == 0.0

        # checking that the total score is correct
        # hardcoded above
        L = len(VIDEO_FIELDS)
        rng = range(1, L + 1)
        assert np.allclose(
            v1r['score'],
            np.dot(
                np.array(rng) - 50,
                np.array(rng) + 10))
        assert np.allclose(
            v2r['score'],
            np.dot(
                np.array(rng) - 50,
                np.array(rng) + 20))

        v1.delete()
        v2.delete()

        # not testing Raw Youtube Search
        # not to make Google angry

        return True

    def test_user_preferences(self, client, current_user_preferences):
        r = client.get("/api/v2/user_preferences/my/", follow=True)
        assert r.status_code == 200

        def assert_json_matches_preferences(prefs, s):
            """Check that user preferences match a json string from API."""
            for f in VIDEO_FIELDS:
                assert np.allclose(getattr(prefs, f), s[f])
            assert prefs.username == s['username']

        # checking that the data from API matches
        assert_json_matches_preferences(current_user_preferences, r.json())

        # new preferences
        data = {f: round(100 * np.random.rand(), 2) for f in VIDEO_FIELDS}

        # should have no effect
        data['username'] = 'xxx'
        data['id'] = 123123123

        # changing my preferences
        r = with_redirect(
            client.patch)(
            "/api/v2/user_preferences/my/",
            data=data)
        assert r.status_code == 200

        current_user_preferences.refresh_from_db()

        assert current_user_preferences.username != data['username']
        data['username'] = current_user_preferences.username

        # must match the new preferences.
        assert_json_matches_preferences(current_user_preferences, data)

        # creating a user that is not us
        u_created, prefs = create_users(name='jon', password='1234')
        id_disallow = prefs.id

        # can't get their preferences
        assert client.get(
            f"/api/v2/user_preferences/{id_disallow}/").status_code == 404

        # and can't set them
        assert client.patch(
            f"/api/v2/user_preferences/{id_disallow}/").status_code == 404

        u_created.delete()

    def test_video_ratings(self, client, current_user_preferences):
        # creating a second user
        u_created, prefs = create_users(
            name='neo', password='followthewhiterabbit')

        # creating some videos
        videos = []
        for video_id in range(1, 1 + 5):
            v = Video.objects.create(
                video_id=str(video_id),
                name=str(video_id),
                publication_date=datetime.date(
                    year=2050,
                    month=1,
                    day=4),
                uploader='morpheus',
                duration=datetime.timedelta(
                    minutes=10),
                views=42)
            videos.append(v)
        video_ids = [v.video_id for v in videos]

        # trying to get a video to rate
        r = client.get(
            '/api/v2/expert_ratings/sample_video/',
            data={
                'only_rated': False})
        assert r.status_code == 200
        r = r.json()
        assert 'video_id' in r

        # trying to get the video object (should work)
        assert Video.objects.get(video_id=r['video_id'])

        # trying to get a rating results in an error
        assert client.get('/api/v2/expert_ratings/1/').status_code == 404

        # checking that we can list ratings
        r = client.get('/api/v2/expert_ratings/')
        assert r.status_code == 200
        assert len(r.json()['results']) == 0

        # creating a rating for someone else results in an error
        assert client.post('/api/v2/expert_ratings/',
                           data={'user': u_created.id}).status_code == 400

        # posting a rating where two videos are equal
        assert client.post(
            '/api/v2/expert_ratings/',
            data={
                'video_1': videos[0].video_id,
                'video_2': videos[0].video_id}).status_code == 400

        data = {'video_1': video_ids[0], 'video_2': video_ids[1]}
        data.update({k: v for k, v in zip(
            VIDEO_FIELDS, range(1, 1 + len(VIDEO_FIELDS)))})

        # posting a normal rating
        assert client.post(
            '/api/v2/expert_ratings/',
            data=data).status_code == 201

        # v12 -> v21 should not be allowed
        data['video_1'], data['video_2'] = data['video_2'], data['video_1']
        assert client.post(
            '/api/v2/expert_ratings/',
            data=data).status_code == 400

        # return

        print(ExpertRating.objects.all())
        rating = ExpertRating.objects.get(video_1=videos[0], video_2=videos[1])

        # now doubling down
        f = VIDEO_FIELDS[0]
        res = client.patch('/api/v2/expert_ratings/double_down/',
                           QUERY_STRING=query_string({'video_left': video_ids[0],
                                                      'video_right': video_ids[1],
                                                      'feature': f}))
        print(res.data, res)
        assert res.status_code == 200

        # feature values: old and new
        vold = getattr(rating, f + "_weight")
        rating.refresh_from_db()
        vnew = getattr(rating, f + "_weight")

        # checking the value
        assert vnew > vold

        # now updating features: "normal" order
        res = client.patch('/api/v2/expert_ratings/by_video_ids/?' + query_string(
            {'video_left': video_ids[0], 'video_right': video_ids[1]}), data={f: 11})
        assert res.status_code == 200, (f, res.json())
        rating.refresh_from_db()
        assert getattr(rating, f) == 11

        # and now the reversed order
        res = client.patch('/api/v2/expert_ratings/by_video_ids/?' + query_string(
            {'video_left': video_ids[1], 'video_right': video_ids[0]}), data={f: 11})
        assert res.status_code == 200, res.json()
        rating.refresh_from_db()
        assert getattr(rating, f) == 100 - 11

        # and now just setting fields
        res = client.patch(
            '/api/v2/expert_ratings/by_video_ids/?' + query_string({'video_left': video_ids[0],
                                                                    'video_right': video_ids[1]}),
            data={f: 100, VIDEO_FIELDS[-1] + "_weight": 8})

        assert res.status_code == 200
        rating.refresh_from_db()
        assert getattr(rating, f) == 100
        assert getattr(rating, VIDEO_FIELDS[-1] + "_weight") == 8

        zero1pl_others = {k: 50 for k in VIDEO_FIELDS[1:]}

        # clear existing
        ExpertRating.objects.filter(user=current_user_preferences).delete()

        # now adding some more ratings for another user
        obj = ExpertRating.objects.create(
            user=prefs, video_1=videos[0], video_2=videos[1], **{f: 50}, **zero1pl_others)
        obj.save()

        def submit_with_f0(v1id, v2id, val):
            """Submit rating from test user with feature 0 = val."""
            # and for the test user
            res = client.post('/api/v2/expert_ratings/',
                              data={'video_1': v1id, 'video_2': v2id,
                                    f: val, **zero1pl_others})
            assert res.status_code in [200, 201], res.data

        submit_with_f0(0, 1, 0)  # 0 is better than 1
        submit_with_f0(1, 2, 0)  # 1 is better than 2
        submit_with_f0(2, 0, 0)  # 2 is better than 0

        # checking inconsistencies
        r = client.get('/api/v2/expert_ratings/inconsistencies/')
        assert r.status_code == 200
        inconsistencies = r.json()['results']
        assert len(inconsistencies) == 1
        inc = inconsistencies[0]
        assert inc['feature'] == f
        assert set(inc['videos']) == set('1201')
        assert set([x['id'] for x in inc['comparisons']]) == {4, 3, 5}

        # querying by videos
        r = client.get('/api/v2/expert_ratings/', data={'video__video_id': 0})
        assert r.status_code == 200
        print(r.json())
        assert len(r.json()['results']) == 2  # only 2 by me

        r = client.get('/api/v2/expert_ratings/', data={'video_1': 0})
        assert r.status_code == 200
        print(r.json())
        assert len(r.json()['results']) == 1  # only 1 by me

        r = client.get('/api/v2/expert_ratings/', data={'video_2': 0})
        assert r.status_code == 200
        print(r.json())
        assert len(r.json()['results']) == 1  # only 1 by me

        r = client.get('/api/v2/expert_ratings/', data={'video_2': 0,
                                                        'video_1': 0})
        assert r.status_code == 200
        print(r.json())
        assert len(r.json()['results']) == 0  # none like this

        # switching user
        client.logout()
        client.login(username='neo', password='followthewhiterabbit')

        # querying by videos
        r = client.get('/api/v2/expert_ratings/', data={'video__video_id': 1})
        assert r.status_code == 200
        print(r.json())

        assert len(r.json()['results']) == 1  # only 2 by new user

        client.logout()

        # deleting
        u_created.delete()
        Video.objects.all().delete()
        ExpertRating.objects.all().delete()

    def test_video_reports(self, client, current_user_preferences):
        # creating a video
        v = Video.objects.create(video_id="aba")
        data = {f: np.random.choice([0, 1]) for f in VIDEO_REPORT_FIELDS}
        data.update({'video': v.video_id,
                     'explanation': "too long didn't watch"})
        r = client.post('/api/v2/video_reports/', data=data)
        assert r.status_code == 201, r.json()
        assert 1 == VideoReports.objects.all().count()
        report = VideoReports.objects.get()

        def report_equals_json(report, data):
            for key, val in data.items():
                val1 = getattr(report, key)
                if key == 'video':
                    val1 = val1.video_id
                assert val == val1

        report_equals_json(report, data)

        data.update({f: np.random.choice([0, 1]) for f in VIDEO_REPORT_FIELDS})
        data['explanation'] = "sdfsdfsdfsdf"
        r = client.patch(f'/api/v2/video_reports/{report.id}/', data=data)
        assert r.status_code == 200, r.json()

        report.refresh_from_db()
        report_equals_json(report, data)

        # getting the report from API
        r = client.get(
            '/api/v2/video_reports/',
            data={
                'video_id': v.video_id})
        assert r.status_code == 200
        assert len(r.json()['results']) == 1

        # don't want to show usernames in reports
        assert 'user' not in r.json()['results'][0]
        assert 'username' not in r.json()['results'][0]

        # can't change another person's report
        other_user_django = DjangoUser.objects.create(username="report_test")
        other_user_up = UserPreferences.objects.create(user=other_user_django)

        r = VideoReports.objects.create(user=other_user_up, video=v, explanation="test")
        report_id = VideoReports.objects.get(user=other_user_up, video=v).id

        resp = client.patch(f'/api/v2/video_reports/{report_id}/',
                            data={'explanation': "test_nnnn"})
        print(resp.status_code)
        assert resp.status_code == 400, r.json()

        r.refresh_from_db()
        assert r.explanation == "test"

        Video.objects.all().delete()
        VideoReports.objects.all().delete()
        other_user_django.delete()

    def test_anonymous_comments(self, client, current_user_preferences):
        u = DjangoUser.objects.create_user(
            username="u_other",
            password="u_other_pass",
            is_active=True)
        UserPreferences.objects.create(user=u)
        UserInformation.objects.create(user=u)
        EmailDomain.objects.create(
            domain="@accepted.org",
            status=EmailDomain.STATUS_ACCEPTED)
        ui_selenium = UserInformation.objects.create(
            user=current_user_preferences.user)
        VerifiableEmail.objects.create(
            user=ui_selenium,
            email="test@accepted.org",
            is_verified=True)
        v = Video.objects.create(video_id="xyz")

        # creating as for myself
        r = client.post('/api/v2/video_comments/', data={'video': v.video_id,
                                                         'comment': 'abc_anon',
                                                         'anonymous': True})
        assert r.status_code == 201

        # i can see my username
        r = client.get(
            '/api/v2/video_comments/',
            data={
                'video_id': v.video_id})
        assert r.status_code == 200
        assert len(r.json()['results']) == 1
        assert r.json()[
                   'results'][0]['username'] == current_user_preferences.user.username

        # other user can't see the username
        client.login(username="u_other", password="u_other_pass")
        r = client.get(
            '/api/v2/video_comments/',
            data={
                'video_id': v.video_id})
        assert r.status_code == 200
        assert len(r.json()['results']) == 1
        assert r.json()['results'][0]['username'] == ""
        assert r.json()['results'][0]['user'] == -1

        client.logout()

        u.delete()
        ui_selenium.delete()
        Video.objects.all().delete()

    def test_comments(self, client, current_user_preferences):
        v = Video.objects.create(video_id="vid1")

        f = VIDEO_FIELDS[0]

        # now have zero comments
        r = client.get(
            '/api/v2/video_comments/',
            data={
                'video_id': v.video_id})
        assert r.status_code == 200
        assert len(r.json()['results']) == 0

        # creating a comment
        r = client.post("/api/v2/video_comments/", data={'video': v.video_id,
                                                         'comment': "testing",
                                                         f: True})
        assert r.status_code == 201, r.json()
        comment_created = r.json()
        first_comment = VideoComment.objects.get()

        # now have one comment
        r = client.get(
            '/api/v2/video_comments/',
            data={
                'video_id': v.video_id})
        assert r.status_code == 200
        assert len(r.json()['results']) == 1

        # creating a child comment
        r = client.post(
            "/api/v2/video_comments/",
            data={
                'video': v.video_id,
                'comment': "testing in child",
                'parent_comment': comment_created['id']})
        assert r.status_code == 201, r.json()

        # checking if it exists
        second_comment = VideoComment.objects.get(parent_comment=first_comment)
        assert first_comment and second_comment
        assert first_comment.children == 1 and second_comment.children == 0

        # getting by parent and checking id
        r = client.get('/api/v2/video_comments/',
                       data={'parent_comment': first_comment.id})
        assert r.status_code == 200, r.json()
        assert r.json()['results'][0]['id'] == second_comment.id

        # changing the comment body
        c = first_comment
        r = client.patch(
            f'/api/v2/video_comments/{c.id}/',
            data={
                'comment': "my new data"})
        assert r.status_code == 200
        c.refresh_from_db()
        assert c.comment == "my new data"
        assert getattr(c, f)  # attribute is currently true

        # changing attribute
        r = client.patch(f'/api/v2/video_comments/{c.id}/', data={f: False})
        assert r.status_code == 200
        c.refresh_from_db()
        assert not getattr(c, f)

        # voting up/down
        for field in VideoCommentMarker.MARKER_CHOICES_1:
            # initially start from 0
            c.refresh_from_db()
            assert getattr(c, field) == 0

            # can't go down
            r = client.post(
                f'/api/v2/video_comments/{c.id}/set_mark/?' +
                query_string(
                    {
                        'marker': field,
                        'action': 'delete'}))
            assert r.status_code == 422

            # changing attribute
            r = client.post(
                f'/api/v2/video_comments/{c.id}/set_mark/?' +
                query_string(
                    {
                        'marker': field,
                        'action': 'add'}))
            assert r.status_code == 201

            # now went up
            c.refresh_from_db()
            assert getattr(c, field) == 1

            # changing attribute
            r = client.post(
                f'/api/v2/video_comments/{c.id}/set_mark/?' +
                query_string(
                    {
                        'marker': field,
                        'action': 'delete'}))
            assert r.status_code == 201

            # now again 0
            c.refresh_from_db()
            assert getattr(c, field) == 0
            print(field)

            # can't delete again
            r = client.post(
                f'/api/v2/video_comments/{c.id}/set_mark/?' +
                query_string(
                    {
                        'marker': field,
                        'action': 'delete'}))
            assert r.status_code == 422

        VideoComment.objects.all().delete()
        Video.objects.all().delete()

    def test_video_rating(self, client, current_user_preferences):
        # creating a video and a rating entry
        data = {k: np.random.randn() for k in VIDEO_FIELDS}
        v = Video.objects.create(video_id="test")
        rating = VideoRating.objects.create(
            video=v, user=current_user_preferences, **data)

        # setting some random preferences
        for k in VIDEO_FIELDS:
            setattr(current_user_preferences, k, np.random.randn())
            current_user_preferences.save()

        # trying to get the rating
        r = client.get('/api/v2/video_ratings/')
        assert r.status_code == 200
        assert len(r.json()['results']) == 1

        # now trying to get it with the video parameter
        r = client.get('/api/v2/video_ratings/', data={'video_id': v.video_id})
        assert r.status_code == 200
        assert len(r.json()['results']) == 1

        res = r.json()['results'][0]

        # now checking that we got all the fields correctly
        for k in VIDEO_FIELDS:
            assert np.allclose(getattr(rating, k), res[k])

        # checking the result
        user_vec = current_user_preferences.features_as_vector_centered
        pref_vec = [res[k] for k in VIDEO_FIELDS]

        assert np.allclose(res['score'], np.dot(user_vec, pref_vec))

        print(res)

    def test_video_list_raters(self, client, current_user_preferences):
        # creating many experts
        from backend.api_v2.videos import N_PUBLIC_CONTRIBUTORS_SHOW
        usernames = [f"expert_{i}" for i in range(10 * N_PUBLIC_CONTRIBUTORS_SHOW)]

        additional_experts, additional_experts_prefs = \
            zip(*[create_users(username, "test") for username in usernames])

        domain_certified = "@certified.com"
        domain_rejected = "@rejected.com"
        EmailDomain.objects.create(domain=domain_certified,
                                   status=EmailDomain.STATUS_ACCEPTED)
        EmailDomain.objects.create(domain=domain_rejected,
                                   status=EmailDomain.STATUS_REJECTED)

        domains_lst = [domain_certified, domain_rejected]

        show_publicly = [np.random.choice([True, False]) for _ in additional_experts]

        additional_experts_info = [UserInformation.objects.create(user=u,
                                                                  show_my_profile=show)
                                   for u, show in
                                   zip(additional_experts, show_publicly)]

        domains = [np.random.choice(domains_lst) for _ in additional_experts]
        is_certified_truth = [domain == domain_certified for domain in domains]
        emails = [VerifiableEmail.objects.create(email="test" + domain,
                                                 user=u,
                                                 is_verified=True)
                  for u, domain in zip(additional_experts_info, domains)]

        # checking that experts have correct status
        is_certified_db = [
            UserInformation.objects.get(user__username=username).is_certified
            for username in usernames]

        assert all([x == y for x, y in zip(is_certified_truth, is_certified_db)]), \
            (is_certified_db, is_certified_truth)

        # creating some videos
        n_videos = 10
        videos = [Video.objects.create(video_id=f"{i}", name="test",
                                       reliability=1) for i in range(n_videos)]

        unique_pairs = [(i, j) for i in range(n_videos) for j in range(n_videos)
                        if i < j]

        n_ratings_max = 10
        assert n_ratings_max <= len(unique_pairs)

        for expert in additional_experts_prefs:
            n_ratings_expert = np.random.choice(range(1, n_ratings_max + 1))
            pairs_idx_chosen = np.random.choice(range(len(unique_pairs)),
                                                n_ratings_expert,
                                                replace=False)
            rating_fields = {x: np.random.randn() for x in VIDEO_FIELDS}

            for pair_idx in pairs_idx_chosen:
                i, j = unique_pairs[pair_idx]
                video1, video2 = videos[i], videos[j]
                ExpertRating.objects.create(user=expert,
                                            video_1=video1,
                                            video_2=video2,
                                            **rating_fields)

        r = client.get('/api/v2/videos/')
        assert r.status_code == 200

        for video_result in r.json()['results']:
            video = Video.objects.get(id=video_result['id'])
            usernames = [x['username'] for x in video_result['public_experts']]
            public_experts = UserInformation.objects.filter(user__username__in=usernames)
            if video_result['n_public_experts']:
                assert public_experts.count() > 0
            total_raters = video_result['n_public_experts'] + video_result['n_private_experts']
            assert total_raters == video.certified_top_raters().count()
            for expert in public_experts:
                assert expert.is_certified
                assert expert.show_my_profile

        for ae in additional_experts:
            ae.delete()

        for v in videos:
            v.delete()

        del emails

    def test_rate_later(self, client, current_user_preferences):
        from backend.models import VideoRateLater
        # checking that the rate later list is empty

        # adding some videos
        v1 = Video.objects.create(video_id="a")
        v2 = Video.objects.create(video_id="b")

        # creating a separate user
        ou = DjangoUser.objects.create(username="other_user", is_active=True)
        oup = UserPreferences.objects.create(user=ou)

        # filling rate later for the other user
        vrl_foreign = VideoRateLater.objects.create(user=oup, video=v1)

        r = client.get('/api/v2/rate_later/')
        assert r.status_code == 200
        assert r.json()['count'] == 0

        # now creating one for myself
        VideoRateLater.objects.create(user=current_user_preferences, video=v1)

        r = client.get('/api/v2/rate_later/')
        assert r.status_code == 200
        assert r.json()['count'] == 1
        assert r.json()['results'][0]['video'] == 'a'

        # adding another one and checkin sorting
        VideoRateLater.objects.create(user=current_user_preferences, video=v2)

        r = client.get('/api/v2/rate_later/')
        assert r.status_code == 200
        assert r.json()['count'] == 2
        assert r.json()['results'][0]['video'] == 'b'
        assert r.json()['results'][1]['video'] == 'a'

        # checking search params
        r = client.get('/api/v2/rate_later/?video__video_id=a')
        assert r.status_code == 200
        assert r.json()['count'] == 1
        assert r.json()['results'][0]['video'] == 'a'

        # deleting via API
        v1_rate_later_id = r.json()['results'][0]['id']
        r = client.delete(f'/api/v2/rate_later/{v1_rate_later_id}/')
        assert r.status_code == 204

        # checking results
        r = client.get('/api/v2/rate_later/')
        assert r.status_code == 200
        assert r.json()['count'] == 1
        assert r.json()['results'][0]['video'] == 'b'

        # check that can't get foreign data
        r = client.get(f'/api/v2/rate_later/{vrl_foreign.id}/')
        assert r.status_code == 404

        # check that can't delete foreign data
        r = client.delete(f'/api/v2/rate_later/{vrl_foreign.id}/')
        assert r.status_code == 404

    def test_wrong_video_id_protection(self, client, current_user_preferences):
        wrong_id = '$$$videoAAA'
        good_id = 'abacaba'
        good_id1 = 'abacabaaa'
        assert good_id != good_id1
        assert not re.match(youtubeVideoIdRegex, wrong_id)
        assert re.match(youtubeVideoIdRegex, good_id)
        assert re.match(youtubeVideoIdRegex, good_id1)

        # List of endpoints where videos can be created:
        # Video POST
        # Expert Ratings POST
        # Expert Rating Set by Video IDS
        # Expert Ratings Slider Value Change
        # Rate later POST

        # VIDEO POST
        r = client.post('/api/v2/videos/', data={'video_id': wrong_id})
        print(r.status_code, r.json())
        assert r.status_code == 400
        assert r.json()['video_id'][0].startswith('Video ID must match')

        # EXPERT RATING, two ways
        r = client.post('/api/v2/expert_ratings/', data={'video_1': wrong_id,
                                                         'video_2': good_id})
        print(r.status_code, r.json())
        assert r.status_code == 400
        assert r.json()['video_1']['video_id'][0].startswith('Video ID must match')

        r = client.post('/api/v2/expert_ratings/', data={'video_1': good_id,
                                                         'video_2': wrong_id})
        print(r.status_code, r.json())
        assert r.status_code == 400
        assert r.json()['video_2']['video_id'][0].startswith('Video ID must match')

        # cleaning videos
        Video.objects.all().delete()

        # creating some good videos
        v1 = Video(video_id=good_id)
        v1.full_clean()
        v1.save()

        v2 = Video(video_id=good_id1)
        v2.full_clean()
        v2.save()

        # creating the rating
        rating = ExpertRating.objects.create(user=current_user_preferences, video_1=v1,
                                             video_2=v2)

        # EXPERT RATING PATCH
        for method in [client.put, client.patch]:
            r = method(f'/api/v2/expert_ratings/{rating.id}/',
                       data={'video_1': wrong_id, 'video_2': good_id1})
            print(r.status_code, r.json())
            assert r.status_code == 400
            assert r.json()['video_1']['video_id'][0].startswith('Video ID must match')

        for method in [client.put, client.patch]:
            r = method(f'/api/v2/expert_ratings/{rating.id}/',
                       data={'video_1': good_id, 'video_2': wrong_id})
            print(r.status_code, r.json())
            assert r.status_code == 400
            assert r.json()['video_2']['video_id'][0].startswith('Video ID must match')

        # EXPERT RATING SET BY VIDEO IDS
        r = client.patch('/api/v2/expert_ratings/by_video_ids/?'
                         f'video_left={good_id}&video_right={good_id1}&force_set_ids=true',
                         data={'video_1': wrong_id, 'video_2': good_id1})
        print(r.status_code, r.json())
        assert r.status_code == 400
        assert r.json()['video_1']['video_id'][0].startswith('Video ID must match')

        r = client.patch('/api/v2/expert_ratings/by_video_ids/?'
                         f'video_left={good_id}&video_right={good_id1}&force_set_ids=true',
                         data={'video_1': good_id, 'video_2': wrong_id})
        print(r.status_code, r.json())
        assert r.status_code == 400
        assert r.json()['video_2']['video_id'][0].startswith('Video ID must match')

        # SLIDER VALUE CHANGE
        r = client.post('/api/v2/expert_ratings/register_slider_change/',
                        data={'video_left': wrong_id, 'video_right': good_id1})
        print(r.status_code, r.json())
        assert r.status_code == 400
        assert r.json()['video_left']['video_id'][0].startswith('Video ID must match')

        r = client.post('/api/v2/expert_ratings/register_slider_change/',
                        data={'video_left': good_id, 'video_right': wrong_id})
        print(r.status_code, r.json())
        assert r.status_code == 400
        assert r.json()['video_right']['video_id'][0].startswith('Video ID must match')

        # RATELATER
        r = client.post('/api/v2/rate_later/',
                        data={'video': wrong_id})
        print(r.status_code, r.json())
        assert r.status_code == 400
        assert r.json()['video']['video_id'][0].startswith('Video ID must match')

    def test_rate_later_bulk_delete(self, client, current_user_preferences):
        from backend.models import VideoRateLater
        import json

        video_ids = ['aba', 'caba', 'xxx', 'zzzz']
        videos = [Video.objects.create(video_id=vid) for vid in video_ids]

        [VideoRateLater.objects.create(user=current_user_preferences,
                                       video=v) for v in videos]

        r = client.patch('/api/v2/rate_later/bulk_delete/',
                         json.dumps([{'video_id': 'aba'},
                                     'caba',
                                     {'video_id': 'xxx'},
                                     {'video_id': 'zzzz'},
                                     'abacabazzz']),
                         content_type='application/json')
        print(r.status_code)
        print(r.status_code, r.json())
        assert r.status_code == 200
        assert r.json()['received'] == 5
        assert r.json()['deleted'] == 4

        assert VideoRateLater.objects.filter(user=current_user_preferences).count() == 0

    def test_online_update_api(self, client, current_user_preferences):
        dj_u_other, other_up = create_users('other_user', 'aba')
        ui_other = UserInformation.objects.create(user=dj_u_other)
        EmailDomain.objects.create(domain='@verified.com', status=EmailDomain.STATUS_ACCEPTED)
        VerifiableEmail.objects.create(user=ui_other, email="other@verified.com",
                                       is_verified=True)

        v1 = Video.objects.create(video_id='online-01', reliability=1)
        v2 = Video.objects.create(video_id='online-02', reliability=2)
        v3 = Video.objects.create(video_id='online-03', reliability=3)
        v4 = Video.objects.create(video_id='online-04', reliability=4)

        VideoRating.objects.create(user=current_user_preferences,
                                   video=v1, reliability=0.5)
        VideoRating.objects.create(user=current_user_preferences,
                                   video=v2, reliability=0.7)
        VideoRating.objects.create(user=current_user_preferences,
                                   video=v3, reliability=0.8)

        VideoRating.objects.create(user=other_up,
                                   video=v1, reliability=0.9)
        VideoRating.objects.create(user=other_up,
                                   video=v2, reliability=0.6)
        VideoRating.objects.create(user=other_up,
                                   video=v4, reliability=0.1)

        ExpertRating.objects.create(user=current_user_preferences, video_1=v1,
                                    video_2=v2, reliability=100)
        ExpertRating.objects.create(user=current_user_preferences, video_1=v2,
                                    video_2=v3, reliability=100)

        ExpertRating.objects.create(user=other_up, video_1=v1,
                                    video_2=v2, reliability=20)
        ExpertRating.objects.create(user=other_up, video_1=v1,
                                    video_2=v4, reliability=0)

        r = client.get('/api/v2/expert_ratings/online_by_video_ids/?video_left=online-00'
                       '&video_right=online-02'
                       '&feature=reliability&new_value=100&add_debug_info=false')
        assert r.status_code == 404

        r = client.get('/api/v2/expert_ratings/online_by_video_ids/?video_left=online-01'
                       '&video_right=online-02'
                       '&feature=reliabasdfasdfility&new_value=100&add_debug_info=false')
        assert r.status_code == 400

        r = client.get('/api/v2/expert_ratings/online_by_video_ids/?video_left=online-01'
                       '&video_right=online-02'
                       '&feature=reliability&new_value=0&add_debug_info=false')
        assert r.status_code == 201
        assert 'debug_info' not in r.json()

        r = client.get('/api/v2/expert_ratings/online_by_video_ids/?video_left=online-01'
                       '&video_right=online-02&add_debug_info=true'
                       '&feature=reliability&new_value=0')
        assert r.status_code == 201
        print(r.json())
        assert all([k in r.json() for k in ['new_score_left', 'new_score_right',
                                            'agg_score_left', 'agg_score_right']])
        debug_info = json.loads(r.json()['debug_info'])
        assert debug_info['saved'] is False
        assert debug_info['other_users'] == 1
        assert debug_info['ratings_in_loss'] == 4
        assert debug_info['videos_in_loss'] == 4

        r = client.patch('/api/v2/expert_ratings/online_by_video_ids/?video_left=online-01'
                         '&video_right=online-02&add_debug_info=true'
                         '&feature=reliability&new_value=0')
        assert r.status_code == 201
        assert all([k in r.json() for k in ['new_score_left', 'new_score_right',
                                            'agg_score_left', 'agg_score_right']])
        assert json.loads(r.json()['debug_info'])['saved'] is True

        Video.objects.filter(video_id__startswith='online').delete()
        dj_u_other.delete()

    def test_expertrating_reverse_order_save(self, client, current_user_preferences):
        v1 = Video.objects.create(video_id="a")
        v2 = Video.objects.create(video_id="b")

        ExpertRating.objects.create(user=current_user_preferences,
                                    video_1=v1,
                                    video_2=v2,
                                    reliability=100)

        r = client.get('/api/v2/expert_ratings/by_video_ids/?video_left=a&video_right=b')
        assert r.status_code == 200
        assert r.json()['reliability'] == 100.0, r.json()

        r = client.get('/api/v2/expert_ratings/by_video_ids/?video_left=b&video_right=a')
        assert r.status_code == 200
        assert r.json()['reliability'] == 0.0, r.json()

        # can't set videos in this mode!
        r = client.patch('/api/v2/expert_ratings/by_video_ids/?video_left=a&video_right=b',
                         {'video_1': 'b', 'video_2': 'a'})
        assert r.status_code == 200

        r = client.get('/api/v2/expert_ratings/by_video_ids/?video_left=a&video_right=b')
        assert r.status_code == 200
        assert r.json()['reliability'] == 100.0, r.json()

    def test_set_all_private(self, client, current_user_preferences):
        v1 = Video.objects.create(video_id="a")
        v2 = Video.objects.create(video_id="b")

        ExpertRating.objects.create(user=current_user_preferences,
                                    video_1=v1,
                                    video_2=v2)

        assert VideoRatingPrivacy.objects.all().count() == 0

        r = client.patch('/api/v2/videos/set_all_rating_privacy/?is_public=false')
        assert r.status_code == 201

        assert VideoRatingPrivacy.objects.all().count() == 2
        assert VideoRatingPrivacy.objects.get(user=current_user_preferences,
                                              video=v1).is_public is False
        assert VideoRatingPrivacy.objects.get(user=current_user_preferences,
                                              video=v2).is_public is False

        r = client.patch('/api/v2/videos/set_all_rating_privacy/?is_public=true')
        assert r.status_code == 201

        assert VideoRatingPrivacy.objects.all().count() == 2
        assert VideoRatingPrivacy.objects.get(user=current_user_preferences,
                                              video=v1).is_public
        assert VideoRatingPrivacy.objects.get(user=current_user_preferences,
                                              video=v2).is_public

    def test_rating_statistics(self, client, current_user_preferences):
        # setting all fields to 0
        for f in VIDEO_FIELDS:
            setattr(current_user_preferences, f, MAX_RATING / 2.)
        current_user_preferences.save()

        # this user would rate publicly
        u1 = DjangoUser.objects.create(username='test1', is_active=True)
        up1 = UserPreferences.objects.create(user=u1)

        # this user would rate privately
        u2 = DjangoUser.objects.create(username='test2', is_active=True)
        up2 = UserPreferences.objects.create(user=u2)

        # two videos + 1 extra
        v1 = Video.objects.create(video_id='v1')
        v2 = Video.objects.create(video_id='v2')
        v3 = Video.objects.create(video_id='v3')

        # everyone has a score for video 1
        VideoRating.objects.create(user=current_user_preferences, video=v1,
                                   reliability=1.0)
        VideoRating.objects.create(user=up1, video=v1,
                                   reliability=2.0)
        VideoRating.objects.create(user=up2, video=v1,
                                   reliability=3.0)

        # everyone has a score for v2
        VideoRating.objects.create(user=current_user_preferences, video=v2,
                                   reliability=4.0)
        VideoRating.objects.create(user=up1, video=v2,
                                   reliability=5.0)
        VideoRating.objects.create(user=up2, video=v2,
                                   reliability=6.0)

        # setting privacy for user 1
        VideoRatingPrivacy.objects.create(video=v1, user=up1, is_public=True)
        VideoRatingPrivacy.objects.create(video=v2, user=up1, is_public=True)

        # setting privacy for user 2
        VideoRatingPrivacy.objects.create(video=v1, user=up2, is_public=False)
        VideoRatingPrivacy.objects.create(video=v2, user=up2, is_public=False)

        # creating some expert ratings to check the n computation
        ExpertRating.objects.create(user=current_user_preferences, video_1=v1, video_2=v2)
        ExpertRating.objects.create(user=up1, video_1=v1, video_2=v2)
        ExpertRating.objects.create(user=up2, video_1=v1, video_2=v2)
        ExpertRating.objects.create(user=current_user_preferences, video_1=v1, video_2=v3)

        # unknown video
        r = client.get('/api/v2/video_ratings/video_rating_statistics/?video__video_id=v3')
        assert r.status_code == 200
        assert r.json()['count'] == 0

        rel_delta = 2.0
        rel = MAX_RATING / 2. + rel_delta

        # all videos -> must get 6 ratings total
        r = client.get(f'/api/v2/video_ratings/video_rating_statistics/'
                       f'?reliability={rel}&limit=100')
        assert r.status_code == 200
        data = r.json()
        assert data['count'] == 6

        # sorting by ID just in case if the API changes
        results = sorted(data['results'], key=lambda x: x['id'])
        assert results[0]['public_username'] == current_user_preferences.user.username, results
        assert results[0]['video'] == v1.video_id, results
        assert results[0]['n_comparisons'] == 2, results  # +extra video
        assert np.allclose(results[0]['score'], rel_delta * 1.0), results
        assert results[1]['public_username'] == u1.username, results
        assert results[1]['video'] == v1.video_id, results
        assert results[1]['n_comparisons'] == 1, results
        assert np.allclose(results[1]['score'], rel_delta * 2.0), results
        assert results[2]['public_username'] is None, results
        assert results[2]['video'] == v1.video_id, results
        assert results[2]['n_comparisons'] == 1, results
        assert np.allclose(results[2]['score'], rel_delta * 3.0), results

        assert results[3]['public_username'] == current_user_preferences.user.username, results
        assert results[3]['video'] == v2.video_id, results
        assert results[3]['n_comparisons'] == 1, results  # +extra video
        assert np.allclose(results[3]['score'], rel_delta * 4.0), results
        assert results[4]['public_username'] == u1.username, results
        assert results[4]['video'] == v2.video_id, results
        assert results[4]['n_comparisons'] == 1, results
        assert np.allclose(results[4]['score'], rel_delta * 5.0), results
        assert results[5]['public_username'] is None, results
        assert results[5]['video'] == v2.video_id, results
        assert results[5]['n_comparisons'] == 1, results
        assert np.allclose(results[5]['score'], rel_delta * 6.0), results
