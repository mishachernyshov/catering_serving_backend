"""
User administration module.
"""
from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from user.models import UserProfile

User = get_user_model()


class UserProfileInline(admin.StackedInline):
    """
    Inline admin interface for UserProfile model.
    """

    model = UserProfile
    can_delete = False


class UserAdmin(BaseUserAdmin):
    """
    Admin interface for the User model.
    """

    inlines = (UserProfileInline,)


try:
    admin.site.unregister(User)
    admin.site.unregister(Group)
except NotRegistered:
    pass
admin.site.register(User, UserAdmin)
