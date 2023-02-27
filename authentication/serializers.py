from dj_rest_auth import serializers as dj_serializers
from rest_framework import serializers


class LoginSerializer(dj_serializers.LoginSerializer):
    email = serializers.EmailField(required=False)

    def get_fields(self):
        fields = super().get_fields()
        fields['username'] = None
        fields['email'] = serializers.CharField(required=False)
        return fields
