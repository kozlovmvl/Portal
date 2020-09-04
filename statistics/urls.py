from django.urls import path

from .views import result_statistics

urlpatterns = [
    path('statistics/result/', result_statistics),
]
