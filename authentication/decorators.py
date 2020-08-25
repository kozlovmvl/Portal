from django.conf import settings
from django.utils import timezone
from rest_framework.response import Response

from .models import CustomUser


def auth_and_parse(func):
    def wrapped(request):
        if 'HTTP_AUTHORIZATION' not in request.META:
            return Response(data={}, status=401)
        try:
            user = CustomUser.objects.get(token=__parse_token(request))
        except CustomUser.DoesNotExist:
            return Response(data={}, status=401)
        if not user.is_active or __is_expire_token(user.date_token_renewed):
            return Response(data={}, status=401)
        system = {'__user': user, 'query': request.GET}
        data = request.POST
        response, status = func(system, data)
        return Response(data=response, status=status)
    return wrapped


def __parse_token(request):
    return request.META['HTTP_AUTHORIZATION'].split(' ')[-1]


def __is_expire_token(created_time_token):
    return timezone.now() - created_time_token \
           > timezone.timedelta(hours=settings.TOKEN_EXPIRE)
