from django.db import models

# Create your models here.
class Comment(models.Model):
    writer = models.ForeignKey('auth.user', related_name='comment_writer', on_delete=models.CASCADE, null=False)
    article_id = models.IntegerField(null=False)
    content = models.TextField(null=False, blank=False)

