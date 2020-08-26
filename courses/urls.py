from django.urls import path
from courses.views import *

urlpatterns = [
    path('folder/get/', get_folders),
    path('document/get/', get_document),
    path('document/like/', like_document),
]