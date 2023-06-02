from django.db import models


# Create your models here.
def receipt_upload_dir(_: "Receipt", filename: str):
    return f'receipts/{Receipt.objects.count()}/{filename}'


class AdminConfig(models.Model):
    receipt_usage_count = models.PositiveIntegerField(default=50)

    def save(self, *args, **kwargs):
        self.__class__.objects.exclude(id=self.id).delete()
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        try:
            return cls.objects.get()
        except cls.DoesNotExist:
            return cls().save()


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
