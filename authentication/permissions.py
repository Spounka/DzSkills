from rest_framework.permissions import BasePermission


class IsAdminOrEdittingSelf(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)
