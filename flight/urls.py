from django.conf.urls import include, url
from django.urls import path, re_path
from rest_framework.routers import DefaultRouter
from .views import (
    FlightViewSet
    )
router = DefaultRouter()
router.register(r'flight', FlightViewSet, base_name='api_v1_flight')
urlpatterns = []
urlpatterns += router.urls
