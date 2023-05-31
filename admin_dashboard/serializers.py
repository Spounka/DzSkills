from rest_framework import serializers
from . import models


class AdminConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AdminConfig
        exclude = ["pk", ]


class ReceiptSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = models.Receipt
        fields = "__all__"

    def get_image(self, receipt):
        request = self.context.get('request')
        url = receipt.image.url
        # return request.build_absolute_uri(url)
        return receipt.image.url


class CreateReceiptSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        if not models.Receipt.objects.filter(is_current=True).first():
            validated_data['is_current'] = True
        return super().create(validated_data)

    class Meta:
        model = models.Receipt
        fields = ["image", ]
