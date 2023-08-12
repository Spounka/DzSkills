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


class AdminConfigUpdateSerializer(serializers.ModelSerializer):
    main_title_text = TitleScreenTextSerializer()
    secondary_title_text = TitleScreenTextSerializer()
    certificate_template = CertificateTemplateSerializer()
    images = LandingPageImageSerializer(many=True, required=False)

    def update(self, instance: models.AdminConfig, validated_data):
        images = validated_data.pop('images', [])
        main_text = validated_data.get('main_title_text', None)
        secondary_text = validated_data.get('secondary_title_text', None)
        certificate_template = validated_data.get('certificate_template', None)

        if instance.main_title_text is None:
            instance.main_title_text = models.TitleScreenText.objects.create()
        if main_text:
            instance.main_title_text.content = main_text['content']
            instance.main_title_text.color = main_text['color']
            instance.main_title_text.save()

        if instance.secondary_title_text is None:
            instance.secondary_title_text = models.TitleScreenText.objects.create()
        if secondary_text:
            instance.secondary_title_text.content = secondary_text['content']
            instance.secondary_title_text.color = secondary_text['color']
            instance.secondary_title_text.save()

        # for i, image in enumerate(images):
        #     img = instance.images.filter(image=image)
        #     if img.exists():
        #         img.first().image = image
        #         img.first().save()
        if instance.certificate_template is None:
            instance.certificate_template = models.CertificateTemplate.objects.create()
        if certificate_template:
            instance.certificate_template.template = certificate_template['template']
            instance.certificate_template.save()
        instance.save()
        return instance

    class Meta:
        model = models.AdminConfig
        exclude = ["id", ]


class AdminConfigSerializer(serializers.ModelSerializer):
    main_title_text = TitleScreenTextSerializer()
    secondary_title_text = TitleScreenTextSerializer()
    certificate_template = CertificateTemplateSerializer()
    images = LandingPageImageSerializer(many=True)

    def update(self, instance, validated_data):
        x = validated_data
        return super().update(instance, validated_data)

    class Meta:
        model = models.AdminConfig
        exclude = ["id", ]


class ReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Receipt
        read_only_fields = ['count', 'is_current']
        fields = "__all__"


class ReceiptsListDeleteSerializer(serializers.Serializer):
    receipts = serializers.ListSerializer(child=serializers.IntegerField(), required=True)


class CreateReceiptSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        if not models.Receipt.objects.filter(is_current=True).first():
            validated_data['is_current'] = True
        return super().create(validated_data)

    class Meta:
        model = models.Receipt
        fields = ["image", ]


class LandingPageRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LandingPageRating
        fields = '__all__'
