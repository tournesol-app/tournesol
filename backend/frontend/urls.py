from django.urls import path, re_path
from . import views


urlpatterns = [
    path('email_verify', views.email_verify),
    path('set_password_login/', views.set_password_login),
    path('welcome/', views.login_by_reset_password_token),
    path('tournesol.latest.csv.zip', views.download_all),
    path('my_tournesol_data.zip', views.download_user_data),
    re_path('.*', views.index),
]
