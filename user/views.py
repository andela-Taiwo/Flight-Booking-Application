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

from rest_auth.views import LoginView
from rest_framework import (
    viewsets,
    decorators
)
import user.services as user_service
from .serializers import (
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

    @decorators.action(methods=['post'], detail=False, url_path='upload')
    def upload_profile_picture(self, request, **kwargs):
        # user_id = kwargs.get('pk')
        try:
            profile_picture = request.FILES['picture']
        except:
            profile_picture = None
        profile = user_service.upload_profile_picture(
            data=request.data,
            requestor=request.user, 
            file=profile_picture
        )
        return FlightBoookingAPIResponse(FileUploadSerializer(profile).data)

    # @decorators.action(methods=['put'], detail=False, url_path='upload/(?P<upload_id>[0-9]+)')
    # def update_profile_picture(self, request, **kwargs):
    #     import pdb; pdb.set_trace()
    #     try:
    #         profile_picture = request.FILES['picture']
    #     except:
    #         profile_picture = None
    #     profile = user_service.update_profile_picture(
    #         requestor=request.user,
    #         file=profile_picture,
    #         upload_id=kwargs.get('upload_id')
          
    #     )
    #     return FlightBoookingAPIResponse(FileUploadSerializer(profile).data)

    # @decorators.action(methods=['delete'], detail=False, url_path='upload/(?P<upload_id>[0-9]+)')
    # def delete_profile_picture(self, request, **kwargs):
        # try:
        #     profile_picture = request.FILES['picture']
        # except:
        #     profile_picture = None
        # profile = user_service.delete_profile_picture(
        #     requestor=request.user,
        #     file=profile_picture,
        #     upload_id=kwargs.get('upload_id')
          
        # )
        # return FlightBoookingAPIResponse(FileUploadSerializer(profile).data)

    
class UploadViewSet(viewsets.ViewSet):
    def post(self, request, **kwargs):
        # user_id = kwargs.get('pk')
        try:
            profile_picture = request.FILES['picture']
        except:
            profile_picture = None
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
            profile_picture = None
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




class VerifyEmailView(APIView):
    permission_classes = (AllowAny,)
    allowed_methods = ('POST', 'OPTIONS', 'HEAD')

    def get_serializer(self, *args, **kwargs):
        return VerifyEmailSerializer(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.kwargs['key'] = serializer.validated_data['key']
        try:
            confirmation = self.get_object()
            confirmation.confirm(self.request)
            return Response({'detail': _('Successfully confirmed email.')}, status=status.HTTP_200_OK)
        except EmailConfirmation.DoesNotExist:
            return Response({'detail': _('Error. Incorrect key.')}, status=status.HTTP_404_NOT_FOUND)


    def get_object(self, queryset=None):
        key = self.kwargs['key']
        emailconfirmation = EmailConfirmationHMAC.from_key(key)
        if not emailconfirmation:
            if queryset is None:
                queryset = self.get_queryset()
            try:
                emailconfirmation = queryset.get(key=key.lower())
            except EmailConfirmation.DoesNotExist:
                raise EmailConfirmation.DoesNotExist
        return emailconfirmation

    def get_queryset(self):
        qs = EmailConfirmation.objects.all_valid()
        qs = qs.select_related("email_address__user")
        return qs

class CustomLoginView(LoginView):
    def get_response(self):
        orginal_response = super().get_response()
        mydata = {"message": "You have successfully logged in", "status": "success"}
        orginal_response.data.update(mydata)
        return orginal_response
