import datetime

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from . import models
from django.utils import timezone

UserModel = get_user_model()


class BanSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=UserModel.objects.filter(), required=False)

    class Meta:
        model = models.Ban
        fields = '__all__'

    def create(self, validated_data):
        validated_data['user'] = self.context['user']
        duration = validated_data['duration']
        if duration <= datetime.date.today():
            raise ValidationError({'code': 'date_is_past', 'message': _('Duration cannot be in the past')})
        if validated_data.get('user').is_admin():
            raise ValidationError({'code': 'user_is_admin', 'message': _("You can't ban another admin")})
        return super().create(validated_data)
