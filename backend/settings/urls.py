"""settings URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.http import HttpResponseForbidden
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_registration.api.urls import urlpatterns as original_registration_urlpatterns
from rest_registration.api.views import register, register_email, send_reset_password_link

from tournesol.throttling import GlobalEmailScopeThrottle

# Override throttle_classes on views defined by rest_registration
register.cls.throttle_classes = [GlobalEmailScopeThrottle]
send_reset_password_link.cls.throttle_classes = [GlobalEmailScopeThrottle]
register_email.cls.throttle_classes = [GlobalEmailScopeThrottle]

exclude_patterns = ["login", "logout"]
filtered_registration_urls = [pattern for pattern in original_registration_urlpatterns if pattern.name not in exclude_patterns]

urlpatterns = [
    path('accounts/', include(filtered_registration_urls)),
    path("admin/", admin.site.urls),
    path("monitoring/", include("django_prometheus.urls")),
    path(
        "o/applications/", HttpResponseForbidden, name="create_app"
    ),  # block for create app in oauth (admin only)
    path("o/", include("oauth2_provider.urls", namespace="oauth2_provider")),
    #  API
    path("", include("tournesol.urls")),
    path("", include("faq.urls")),
    #  SWAGGER
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]
