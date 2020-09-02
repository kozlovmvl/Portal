from uuid import uuid1

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class CustomUser(AbstractUser):

    ROLES = [
        (1, 'admin'),
        (2, 'user')
    ]

    token = models.UUIDField('токен', default=uuid1)
    date_token_renewed = models.DateTimeField(default=timezone.now)
    role = models.SmallIntegerField('роль', choices=ROLES)

    @classmethod
    def get_one(cls, user_id):
        try:
            return cls.objects.values('id').get(id=user_id)
        except:
            {'error': 'user not find'}

    def create_token(self):
        self.token = uuid1()
        self.date_token_renewed = timezone.now()
        self.save(update_fields=['token', 'date_token_renewed'])
        return self.token
