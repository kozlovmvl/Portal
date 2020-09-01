from django.urls import path

from tests.views import *

urlpatterns = [
    path('test/all/', test_all),
    path('test/get/', test_get),
    path('attempt/start/', attempt_start),
    path('attempt/finish/', attempt_finish)
]