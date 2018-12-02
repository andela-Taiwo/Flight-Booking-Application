from rest_framework import serializers
from user.models import User, Profile
from rest_auth.serializers import UserDetailsSerializer, PasswordResetSerializer
from rest_auth.registration.serializers import RegisterSerializer
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email

# from rest_auth.serializers import PasswordResetSerializer

from allauth.account.forms import ResetPasswordForm

class PasswordSerializer (PasswordResetSerializer):
    password_reset_form_class = ResetPasswordForm

class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password1', 'password2' )
        extra_kwargs = {'password1': {'write_only': True}, 'password2': {'write_only': True} }

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['email'],
                                        None,
                                        validated_data['password1'])
        return user

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        field = '__all__'

    def save(self, **kwargs):
        profile = self.validated_data.pop('profile')
        instance = super().save(**kwargs)
        Profile.objects.update_or_create(user=instance, defaults=profile)
        return instance

class RegisterSerializerCustom(RegisterSerializer):
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True, write_only=True)
    last_name = serializers.CharField(required=True, write_only=True)
    password1 = serializers.CharField(required=True, write_only=True)
    password2 = serializers.CharField(required=True, write_only=True)
    class Meta:
        model = User
        fields = '__all__'

    def get_cleaned_data(self):
        return {
        'password1': self.validated_data.get('password1', ''),
        'password2': self.validated_data.get('password2', ''),
        'email': self.validated_data.get('email', ''),
        'first_name': self.validated_data.get('first_name', ''),
        'last_name': self.validated_data.get('last_name', ''), 
    }
    
    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        user.first_name = self.cleaned_data['first_name']
        user.last_name  = self.cleaned_data['last_name']
        adapter.save_user(request, user, self)
        setup_user_email(request, user, [])
        user.save()
        return user


class UserSerializer(UserDetailsSerializer):
    type = serializers.CharField(source="profile.type")
    phone = serializers.CharField(source="profile.phone")
    mobile_phone = serializers.CharField(source="profile.mobile_phone")
    address_1 = serializers.CharField(source="profile.address_1")
    address_2 = serializers.CharField(source="profile.address_2")
    city = serializers.CharField(source="profile.city")
    zipcode = serializers.CharField(source="profile.zipcode")
    country = serializers.CharField(source="profile.country")

    class Meta(UserDetailsSerializer.Meta):
        fields = UserDetailsSerializer.Meta.fields + (
            'type',
            'phone',
            'mobile_phone',
            'address_1',
            'address_2',
            'city',
            'zipcode',
            'country',
            )

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        type = profile_data.get('type')
        phone = profile_data.get('phone')
        mobile_phone = profile_data.get('mobile_phone')
        address_1 = profile_data.get('address_1')
        address_2 = profile_data.get('address_2')
        zipcode = profile_data.get('zipcode')
        city = profile_data.get('city')
        country = profile_data.get('country')
        

        instance = super(UserSerializer, self).update(instance, validated_data)

        # get and update user profile
        profile = instance.profile
        if profile_data:
            profile.type = type if type else profile.type
            profile.phone = phone if phone else profile.phone
            profile.mobile_phone = mobile_phone if mobile_phone else profile.mobile_phone
            profile.address_1 = address_1 if address_1 else profile.address_1
            profile.address_2 = address_2 if address_2 else profile.address_2
            profile.zipcode = zipcode if zipcode else profile.zipcode
            profile.city = city if city else profile.city
            profile.country = country if country else profile.country
            profile.save()
        return instance