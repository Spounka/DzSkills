from rest_framework import serializers
from . import models


class TitleScreenTextSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['content', 'color']
        model = models.TitleScreenText
        depth = 0


class CertificateTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['template']
        model = models.CertificateTemplate
        depth = 0


class LandingPageImageSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'image']
        model = models.LandingPageImage
        depth = 0


class AdminConfigSerializer(serializers.ModelSerializer):
    main_title_text = TitleScreenTextSerializer()
    secondary_title_text = TitleScreenTextSerializer()
    certificate_template = CertificateTemplateSerializer()
    images = LandingPageImageSerializer(many=True)

    class Meta:
        model = models.AdminConfig
        exclude = ["id", ]


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
