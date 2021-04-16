"""django_react URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken import views as drf_views

urlpatterns = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) +\
    [
    # admin panel
    path('admin/', admin.site.urls),

    # login into the API
    path('api/', include('rest_framework.urls')),

    # token authentication
    path('api-token-auth/', drf_views.obtain_auth_token),

    # API
    path('api/v2/', include('backend.api_v2.urls')),
    path(
        'schema/',
        SpectacularAPIView.as_view(
            api_version="1.0.0"),
        name='schema'),
    path(
        'schema/swagger-ui/',
        SpectacularSwaggerView().as_view(
            url_name='schema'),
        name='swagger-ui'),
    path(
        'schema/redoc/',
        SpectacularRedocView.as_view(
            url_name='schema'),
        name='redoc'),

    # training artifacts
    path('files/', include('directory.urls')),

    # social media authentication
    path('', include('social_django.urls', namespace='social')),

    # React front-end
    path('', include('frontend.urls')),
]
