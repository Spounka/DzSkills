from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from authentication.permissions import IsAdmin
from . import serializers
from django.shortcuts import render
from rest_framework import response, permissions, decorators, status, generics
import authentication.models as authentication
from . import models

UserModel = get_user_model()


# Create your views here.
@decorators.api_view(['POST'])
@decorators.permission_classes([IsAdmin])
def ban_user(request, pk, *args, **kwargs):
    try:
        user: 'authentication.User' = UserModel.objects.get(pk=pk)
        if user.is_banned():
            return response.Response(status=status.HTTP_400_BAD_REQUEST, data={
                'code': 'ban_exists',
                'message': _(f'User under a running ban until {user.bans.first().duration}')
            })
        serializer = serializers.BanSerializer(data=request.data, context={'user': user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(status=status.HTTP_201_CREATED, data=serializer.data)
    except UserModel.DoesNotExist:
        return response.Response(status=status.HTTP_404_NOT_FOUND, data={
            'code': 'not_found',
            'message': _('No User with such ID exists')
        })
