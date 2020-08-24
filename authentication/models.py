from django.db import models
from uuid import uuid1
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

# Create your models here.


class CustomUser(AbstractUser):
    token = models.UUIDField('Токен', default=uuid1)
    date_token_renewed = models.DateTimeField(default=timezone.now)
