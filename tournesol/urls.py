# coding: utf-8
from django.urls import path, include
from rest_framework import routers

from .views import ComparisonViewSet

router = routers.DefaultRouter()
router.register(r'comparison', ComparisonViewSet)


app_name = 'comparison'
urlpatterns = [
    path('', include(router.urls)),
]