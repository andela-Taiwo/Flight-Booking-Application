from allauth.account.models import EmailConfirmation, EmailConfirmationHMAC
from rest_auth.serializers import PasswordResetConfirmSerializer
from django.contrib.auth import get_user_model
from rest_framework import generics
from django.utils.translation import ugettext_lazy as _
from rest_auth.registration.serializers import VerifyEmailSerializer
from rest_framework import status
from rest_framework.decorators import api_view, APIView
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework import exceptions

from rest_auth.views import LoginView
from rest_framework import (
    viewsets,
    decorators
)
import user.services as user_service
from user.serializers import (
    UserSerializer, 
    ProfileSerializer,
    FileUploadSerializer,
    ViewProfileSerializer
    )
from rest_framework import authentication, permissions
from api.response import FlightBoookingAPIResponse

# Create your views here.
@api_view()
def django_rest_auth_null():
    return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view()
def complete_view(request):
    return Response("Email account is activated")

class UserViewSet(viewsets.ViewSet):
    ''' User Profile views '''

    def retrieve(self, request, *args, **kwargs):
        profile = user_service.retrieve_profile(
            requestor=request.user,
            profile_id=kwargs.get('pk')
        )
        return FlightBoookingAPIResponse(ViewProfileSerializer(profile).data)


    
class UploadViewSet(viewsets.ViewSet):
    def create(self, request):
        try:
            profile_picture = request.FILES['picture']
        except:
            raise exceptions.NotAcceptable(detail='Please select picture to upload')
        profile = user_service.upload_profile_picture(
            data=request.data,
            requestor=request.user, 
            file=profile_picture
        )
        return FlightBoookingAPIResponse(FileUploadSerializer(profile).data)

    def update(self, request, **kwargs):
        try:
            profile_picture = request.FILES['picture']
        except:
            raise exceptions.NotAcceptable(detail='Please select picture to upload')
        profile = user_service.update_profile_picture(
            requestor=request.user,
            file=profile_picture,
            upload_id=kwargs.get('pk')
          
        )
        return FlightBoookingAPIResponse(FileUploadSerializer(profile).data)

    def delete(self, request, **kwargs):
        try:
            profile_picture = request.FILES['picture']
        except:
            profile_picture = None
        profile = user_service.delete_profile_picture(
            requestor=request.user,
            file=profile_picture,
            upload_id=kwargs.get('pk')
          
        )
        return FlightBoookingAPIResponse(FileUploadSerializer(profile).data)

class CustomLoginView(LoginView):
    def get_response(self):
        orginal_response = super().get_response()
        mydata = {"message": "You have successfully logged in", "status": "success"}
        orginal_response.data.update(mydata)
        return orginal_response
