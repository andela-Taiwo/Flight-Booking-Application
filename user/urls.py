from django.conf.urls import include, url
from django.urls import path, re_path
from rest_framework.routers import DefaultRouter
from rest_auth.registration.views import RegisterView
from allauth.account.views import confirm_email, PasswordResetView
from allauth.account.views import ConfirmEmailView
from .views import (
    VerifyEmailView,
    django_rest_auth_null,
    complete_view,
    CustomLoginView, 
    UserViewSet,
    UploadViewSet
    )
router = DefaultRouter()
router.register(r'profile', UserViewSet, base_name='api_v1_profile')
router.register(r'profile/upload', UploadViewSet, base_name='api_v1_profile_upload')
urlpatterns = [
    path('accounts/', include('allauth.urls')),
    path('', include('rest_auth.urls')),
     path('login/', CustomLoginView, name='account_login'),
    re_path(r'registration/account-email-verification-sent/', django_rest_auth_null, name='account_email_verification_sent'),
    path('registration/complete/', complete_view, name='account_confirm_complete'),
    path('registration/', include('rest_auth.registration.urls')),
    path('registration/', RegisterView.as_view(), name='account_signup'),
    re_path(r'^account-confirm-email/(?P<key>[-:\w]+)/', ConfirmEmailView.as_view(),
        name='account_confirm_email'),
]
urlpatterns += router.urls
