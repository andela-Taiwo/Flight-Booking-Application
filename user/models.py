from django.utils.translation import ugettext_lazy as _
from decimal import Decimal
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.db import models
from rest_framework.exceptions import APIException
from django.db.models import Sum
from django.dispatch import receiver
from django.conf import settings
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser, BaseUserManager
from api.soft_deletion_model import SoftDeletionModel

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, **fields):
        """
        Create and save a user with the given username, email, and password.
        """
        email = fields.pop('email')
        password = fields.get('password1')
        if not email:
            raise ValueError("Email address is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, **fields):
        fields.setdefault('is_staff', False)
        fields.setdefault('is_superuser', False)

        return self._create_user(**fields)

    def create_superuser(self, **fields):
        fields.setdefault('is_staff', True)
        fields.setdefault('is_superuser', True)

        if fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(**fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(max_length=50, unique=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    username = models.CharField(max_length=128, blank=True, null=True)
    last_modified = models.DateTimeField(auto_now=True, editable=False)
    password = models.CharField(max_length=128, blank=True, null=True)
    is_staff = models.BooleanField(_('staff status'), default=False,
    help_text=_('Designates whether the user can log into this admin site.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()
    class Meta:
        verbose_name_plural = "All Users"


class Profile(models.Model):
    """ User profile model - main user entry object """

    USER_CLIENT = 0
    USER_ADMIN = 1


    USER_MR = 0
    USER_MS = 1
    USER_MRS = 2
    USER_MISS = 3
    USER_DR = 4

    USER_TYPES = (
        (USER_CLIENT, 'Client'),
        (USER_ADMIN, 'Admin'),
    )
    

    USER_TITLES = (
        (USER_MR, 'Mr.'),
        (USER_MS, 'Ms.'),
        (USER_MRS, 'Mrs.'),
        (USER_MISS, 'Miss.'),
        (USER_DR, 'Dr.')
    )

    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    GENDER_MALE = 1
    GENDER_FEMALE = 2

    title = models.IntegerField(choices=USER_TITLES, default=USER_MR)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    mobile_phone = models.CharField(max_length=50, null=True, blank=True)

    address_1 = models.CharField(max_length=255, null=True, blank=True)
    address_2 = models.CharField(max_length=255, null=True, blank=True)
    address_3 = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    zipcode = models.CharField(max_length=10, null=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    type = models.IntegerField(choices=USER_TYPES, default=USER_CLIENT)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    # profile_picture_name = models.TextField(null=True, blank=True)
    # profile_picture_url = models.TextField(null=True, blank=True)
    # profile_picture_key = models.TextField(null=True, blank=True)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Upload(SoftDeletionModel):
    '''File upload model '''
    profile_picture_name = models.TextField(null=True, blank=True)
    profile_picture_url = models.TextField(null=True, blank=True)
    profile_picture_key = models.TextField(null=True, blank=True)
    profile = models.ForeignKey(
        Profile,
        related_name='profile_picture',
        verbose_name="profile_uploader",
        on_delete=models.PROTECT
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Deleted at'
    )
    def validate_unique(self, exclude=None):
        qs = Upload.objects.filter(profile_picture_key=self.profile_picture_key)
        if self.pk is None:   
            if qs.exists():
                raise APIException(detail='file key already exist')
            
    def save(self, *args, **kwargs):
        self.validate_unique()
        super(Upload, self).save(*args, **kwargs)

