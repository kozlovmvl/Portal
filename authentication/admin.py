from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from authentication.models import *
# Register your models here.

admin.site.register(CustomUser)