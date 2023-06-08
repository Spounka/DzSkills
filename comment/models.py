from django.db import models


# Create your models here.

class Comment(models.Model):
    content = models.CharField(default="", max_length=300)
    commentor = models.ForeignKey('authentication.User', on_delete=models.CASCADE)
    video = models.ForeignKey('courses.Video', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.commentor.username} - {self.video} Comment'
