from django.contrib.auth.models import Group
from rest_framework.permissions import BasePermission


class SuperuserBasePermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser or request.user.is_staff:
            return True
        return self.check_permissions(request, view)

    def check_permissions(self, request, view):
        return False


class IsInGroup(SuperuserBasePermission):
    def __init__(self, group_name=None):
        self.group_name = group_name

    def check_permissions(self, request, view):
        assert self.group_name is not None, "Group Name Empty!"
        return request.user.groups.filter(name=self.group_name).exists()


class IsAdmin(IsInGroup):
    def __init__(self):
        super().__init__(group_name='AdminGroup')


class IsTeacher(IsInGroup):
    def __init__(self):
        super().__init__(group_name='TeacherGroup')


class IsStudent(IsInGroup):
    def __init__(self):
        super().__init__(group_name='StudentGroup')
