from django.contrib.auth.models import Group
from rest_framework.permissions import BasePermission


class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser or request.user.is_staff


class IsAdmin(BasePermission):
    group_name = "AdminGroup"

    def has_permission(self, request, view):
        return request.user.groups.filter(name=self.group_name).exists()
