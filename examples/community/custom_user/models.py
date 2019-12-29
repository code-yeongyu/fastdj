from django.db import models

# Create your models here.
from django.conf import settings
class Profile(models.Model):
    nickname = models.CharField(max_length=10)
    bio = models.TextField()
    website = models.URLField()
    job = models.CharField(max_length=3, default='ETC', choices=[('ST', 'STUDENT'), ('BS', 'BUSINESS MAN'), ('PR', 'PROGRAMMER'), ('ETC', 'ETC')])
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

