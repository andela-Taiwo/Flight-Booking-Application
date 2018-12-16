from django.conf.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter
from django.views.generic import TemplateView

router = DefaultRouter()

urlpatterns = [
    path('', include('user.urls')),
    path('', include('flight.urls'))
]
urlpatterns += router.urls
