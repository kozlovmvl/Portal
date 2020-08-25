from uuid import uuid1

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class CustomUser(AbstractUser):
    token = models.UUIDField('токен', default=uuid1)
    date_token_renewed = models.DateTimeField(default=timezone.now)

    def create_token(self):
        self.token = uuid1()
        self.date_token_renewed = timezone.now()
        self.save(update_fields=['token', 'date_token_renewed'])
        return self.token
