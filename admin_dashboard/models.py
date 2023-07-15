from django.core.exceptions import ValidationError
from django.db import models
import re


# Create your models here.
def receipt_upload_dir(_: "Receipt", filename: str):
    return f'receipts/{Receipt.objects.count()}/{filename}'


def certificate_upload_dir(_: "CertificateTemplate", filename: str) -> str:
    return f'admin/title-screen/certificate/{filename}'


def landing_page_upload_dir(_: "LandingPageImage", filename: str) -> str:
    return f'admin/title-screen/images/{filename}'


def validate_color(value):
    expression = r"^#[0-9a-fA-F]{6}([0-9a-f-A-F]{2}|[0-9a-f-A-F]{4})?$"
    if not re.match(expression, value):
        raise ValidationError("Color invalid")


class TitleScreenText(models.Model):
    content = models.CharField(max_length=300, default="")
    color = models.CharField(max_length=30, default="#000000", validators=[validate_color])


class CertificateTemplate(models.Model):
    template = models.FileField(upload_to=certificate_upload_dir)


class LandingPageImage(models.Model):
    image = models.FileField()
    config = models.ForeignKey('AdminConfig', on_delete=models.CASCADE, null=True, related_name='images')


class ChosenTeacher(models.Model):
    ...


class Comments(models.Model):
    ...


class Receipt(models.Model):
    image = models.FileField(upload_to=receipt_upload_dir)
    count = models.PositiveIntegerField(default=0, blank=True)
    is_current = models.BooleanField(default=False, blank=True)

    def save(self, *args, **kwargs):
        if not self.__class__.objects.filter(is_current=True).first():
            self.is_current = True
        return super().save(*args, **kwargs)

    def increment(self):
        if self.count >= AdminConfig.load().receipt_usage_count:
            self.count = 0
            self.is_current = False
            self.save()

            obj = self.load_next_model(self.pk)

            obj.count = 1
            obj.is_current = True
            obj.save()
            return obj
        else:
            self.count += 1
            self.save()
            return self

    def load_next_model(self, pk):
        try:
            obj = self.__class__.objects.filter(pk__gt=pk).get()
        except self.__class__.MultipleObjectsReturned:
            obj = self.__class__.objects.filter(pk__gt=pk).first()
        except self.__class__.DoesNotExist:
            obj = self.__class__.objects.first()
        return obj


class AdminConfig(models.Model):
    receipt_usage_count = models.PositiveIntegerField(default=50)
    main_title_text = models.ForeignKey(TitleScreenText, on_delete=models.SET_NULL, null=True,
                                        related_name="main_title")
    secondary_title_text = models.ForeignKey(TitleScreenText, on_delete=models.SET_NULL, null=True,
                                             related_name="secondary_title")
    certificate_template = models.ForeignKey(CertificateTemplate, on_delete=models.SET, null=True)

    def save(self, *args, **kwargs):
        self.__class__.objects.exclude(id=self.id).delete()
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        try:
            return cls.objects.get()
        except cls.DoesNotExist:
            return cls().save()
