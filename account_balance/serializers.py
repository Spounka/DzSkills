from . import models
from authentication.models import User
from rest_framework import serializers
from authentication.serializers import UserSerializer


class AccountBalanceSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = models.AccountBalance
        fields = "__all__"
        depth = 1


class MoneyRequestSerializer(serializers.ModelSerializer):
    account = AccountBalanceSerializer(required=False)
    type = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = models.MoneyRequest
        fields = '__all__'

    def create(self, validated_data):
        user: User = self.context['request'].user
        if not hasattr(user, 'accountbalance'):
            user.accountbalance = models.AccountBalance.objects.create(user=user)
            user.save()
        validated_data['account'] = user.accountbalance
        return super().create(validated_data)

    def update(self, instance: models.MoneyRequest, validated_data):
        if validated_data.get('type', None) == 'approve':
            instance.status = instance.APPROVED
        elif validated_data.get('type', None) == 'reject':
            instance.status = instance.REJECTED

        instance.save()
        return instance
