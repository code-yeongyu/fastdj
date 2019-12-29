from django.db import models

# Create your models here.
class Article(models.Model):
    writer = models.ForeignKey('auth.user', related_name='article_writer', on_delete=models.CASCADE, null=False)
    content = models.TextField(null=False, blank=True)
    tag = models.TextField(default="")

