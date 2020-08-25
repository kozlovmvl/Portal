from django.urls import path
from authentication.views import *

urlpatterns = [
    path('signin/', sign_in)
]