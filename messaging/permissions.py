from rest_framework import permissions


class IsOwnerOrReadonly(permissions.BasePermission):
    def __init__(self, obj_attr):
        self.obj_attr = obj_attr

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        owner = getattr(obj, self.obj_attr)
        return owner == request.user
