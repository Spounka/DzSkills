from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.

class Comment(models.Model):
    content = models.CharField(default="", max_length=300, verbose_name=_('Content'))
    commentor = models.ForeignKey('authentication.User', on_delete=models.CASCADE, verbose_name=_('Commentor'))
    video = models.ForeignKey('courses.Video', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.commentor.username} - {self.video} Comment'
