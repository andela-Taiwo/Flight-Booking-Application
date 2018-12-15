import json
from rest_framework.generics import get_object_or_404
from django.contrib.auth.models import User
from rest_framework import exceptions
from rest_framework.exceptions import APIException
from django.db import (
    transaction,
    IntegrityError,
    models
)
from api.s3_services import (
    s3_delete,
    s3_upload,
    s3_presigned_url
)
from user.models import (
  Profile, Upload
)

from user.serializers import ProfileSerializer, FileUploadSerializer



def make_file_key(category, name):
    return 'media/{}/{}'.format(category, name)

# def update_user(requestor, user_id, data):
#     user = get_object_or_404(User, id=user_id)
#     serializer = UserSerializer(
#         user,
#         data=data
#     )
#     if serializer.is_valid(raise_exception=True):
#         serializer.save()
#     return serializer.data

def deserialize_profile(upload, action, data, serializer_class):
    '''Deserialize and validate profile'''
    assert action == 'create' or action == 'update'
 
    serializer = serializer_class(
        instance=upload,
        partial=(action == 'update'),
        data=data
    )
    serializer.is_valid(raise_exception=True)  
    validated_data = serializer.validated_data
    validated_data.pop('uploader', None)
    for name, value in validated_data.items():
        setattr(upload, name, value)
    return upload

def create_or_update_profile_pic(requestor, file, uploaded_profile):
    profile = get_object_or_404(Profile, id=requestor.profile.pk)
    file_key = make_file_key("photo", file.name)
    s3obj = s3_upload(
            filekey=file_key,
            filebody=file.read(), 
            filename=file.name,
            uploader_pk=requestor.profile.pk,
            description='profile'
        )
    
    file_url = s3_presigned_url(file_key)

    try:
        file = Upload.objects.get(profile_picture_key=file_key)
        file.profile = profile
        file.profile_picture_name = file.name
        file.profile_picture_key = file_key
        file.profile_picture_url = file_url
        file.save()
        return file
    except Upload.DoesNotExist:
        # We're uploading this file for the first time
        uploaded_profile.profile = profile
        uploaded_profile.profile_picture_name = file.name
        uploaded_profile.profile_picture_key = file_key
        uploaded_profile.profile_picture_url = file_url
        uploaded_profile.save()
        return uploaded_profile

def upload_profile_picture(requestor, data, file):
    data.pop('picture', None)
    data = data.copy()
    
    if file is None:
        return []
    with transaction.atomic():  
   
        file_key = make_file_key("photo", file.name)
        profile = get_object_or_404(Profile, id=requestor.profile.pk)
        upload = Upload()
        # data['profile'] = profile
        uploaded_profile = deserialize_profile(
                upload=upload,
                action='create',
                data=data,
                serializer_class=FileUploadSerializer
        )
        s3obj = s3_upload(
            filekey=file_key,
            filebody=file.read(), 
            filename=file.name,
            uploader_pk=requestor.profile.pk,
            description='profile'
        )
        file_url = s3_presigned_url(file_key)
        uploaded_profile.profile = profile
        uploaded_profile.profile_picture_name = file.name
        uploaded_profile.profile_picture_key = file_key
        uploaded_profile.profile_picture_url = file_url
        uploaded_profile.save()
    return uploaded_profile

def retrieve_profile_picture(requestor, upload_id):
    profile_pic = get_object_or_404(Upload, id=upload_id)
    if requestor.is_staff or profile_pic.profile.user == requestor:
        return profile_pic
    raise exceptions.PermissionDenied('Not authorized to view the profile')


def delete_profile_picture(requestor, file, upload_id):
    profile_pic = retrieve_profile_picture(requestor, upload_id)
    if requestor.is_staff or requestor == profile_pic.profile.user:
        s3_delete(profile_pic.profile_picture_key)
        return profile_pic.delete()
    raise exceptions.PermissionDenied('Not authorized to perform the action.')

def update_profile_picture(requestor, file, upload_id):
    # if requestor.is_staff or requestor == profile_pic.profile.user:
    profile_pic = retrieve_profile_picture(requestor, upload_id)  
    if file is None:
        return []
    with transaction.atomic():  
        # data['profile'] = profile
        uploaded_profile = deserialize_profile(
                upload=profile_pic,
                action='update',
                data={},
                serializer_class=FileUploadSerializer
        )
        upload = create_or_update_profile_pic(requestor, file, uploaded_profile)
    return upload

def retrieve_profile(requestor, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)

    if requestor.is_staff or requestor.id == profile.user_id:
        return profile
    raise exceptions.PermissionDenied()
