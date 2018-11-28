from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import UserRegistrationForm
# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
from .models import User


class UserAdmin(BaseUserAdmin):
    add_form =  UserRegistrationForm

    list_display = ('email', 'last_name')
    list_filter = ('last_name',)

    fieldsets = (
        (None, {'fields': ( 'email','password')}),

        ('Permissions', {'fields': ('is_admin',)}),
    )

    search_fields =  ( 'email', 'last_name', 'first_name')
    ordering = ('email', 'last_name')

    filter_horizontal = ()

admin.site.register(User, UserAdmin)