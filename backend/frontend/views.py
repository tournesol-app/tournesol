from datetime import datetime
from functools import partial

from backend.management.get_all_dataframes import save_dfs_get_zip, get_user_data, \
    get_public_append_only_database_as_pd
from backend.models import UserPreferences, UserInformation
from backend.reset_password import reset_token
from backend.user_verify import verify_email_by_token
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User as DjangoUser
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import ensure_csrf_cookie
from frontend.helpers import get_id_or_m1, get_user_id_or_m1
from django_react.settings import ENABLE_YOUTUBE_VIDEO_EMBED


def create_user_preferences():
    """A dirty hack to create preferences for new users.

       TODO: replace with a better way, like triggering creation
         when a DjangoUser is created.
    """
    # loop over Django Users
    for user in DjangoUser.objects.all().filter(userpreferences=None):
        try:
            # creating User Preferences for that user
            UserPreferences.objects.get_or_create(user=user)
        except Exception:
            pass

    # loop over Django Users
    for user in DjangoUser.objects.all().filter(userinformation=None):
        try:
            UserInformation.objects.get_or_create(user=user)
        except Exception:
            pass


def template_kwargs(request):
    """Get parameters for templates based on a request."""
    return {'username': request.user.username,
            'user_information_id': get_id_or_m1(UserInformation,
                                                user__username=request.user.username),
            'is_authenticated': 1 if request.user.is_authenticated else 0,
            'is_superuser': 1 if request.user.is_superuser else 0,
            'user_id': get_user_id_or_m1(request),
            'user_preferences_id': get_id_or_m1(UserPreferences,
                                                user__username=request.user.username),
            'ENABLE_YOUTUBE_VIDEO_EMBED': 1 if ENABLE_YOUTUBE_VIDEO_EMBED else 0}


@ensure_csrf_cookie
def index(request):
    # creating preferences for users created from the admin panel
    create_user_preferences()

    return render(request,
                  'frontend/index.html',
                  template_kwargs(request)
                  )


@staff_member_required
def download_all(request):
    """Download the database."""
    zip_file = save_dfs_get_zip()

    name = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    out_zip = f'database_tournesol_{name}.zip'

    response = HttpResponse(zip_file.read(), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=%s' % out_zip
    response['X-Sendfile'] = out_zip

    del zip_file
    return response


@login_required
def download_user_data(request):
    """Download the database."""
    username = request.user.username
    zip_file = save_dfs_get_zip(dfs_fcn=partial(get_user_data, username=username))

    name = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    out_zip = f'tournesol_{username}_{name}.zip'

    response = HttpResponse(zip_file.read(), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=%s' % out_zip
    response['X-Sendfile'] = out_zip

    del zip_file
    return response


def download_public_database(request):
    """Download the PUBLIC database."""
    zip_file = save_dfs_get_zip(dfs_fcn=get_public_append_only_database_as_pd)

    name = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    out_zip = f'tournesol_public_{name}.zip'

    response = HttpResponse(zip_file.read(), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=%s' % out_zip
    response['X-Sendfile'] = out_zip

    del zip_file
    return response


def email_verify(request):
    """Verify an email address."""
    print(request, dir(request))
    token = request.GET.get('token', "")
    try:
        email_verified = verify_email_by_token(token)
        return redirect(f'/email_verified/{email_verified}')
    except ValueError as e:
        return HttpResponse(str(e))


def set_password_login(request):
    """Login by reset password token and redirect to /set_password."""
    print(request, dir(request))
    token = request.GET.get('token', "")
    try:
        user = reset_token(token)
        if user:
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('/set_password')
        return HttpResponse('User not found')
    except ValueError as e:
        return HttpResponse(str(e))


def login_by_reset_password_token(request):
    """Login by reset password token and redirect to /."""
    token = request.GET.get('token', "")
    try:
        user = reset_token(token, delete_token=False)
        if user:
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('/')
        return HttpResponse('User not found')
    except ValueError as e:
        return HttpResponse(str(e))
