from django.http import JsonResponse
from django.utils import timezone
from django.conf import settings

from .models import CustomUser


def auth_and_parse(func):
    def wrapped(request):
        if 'HTTP_AUTHORIZATION' in request.META:
            try:
                user = CustomUser.objects.get(token=__parse_token(request.META['HTTP_AUTHORIZATION']))
            except CustomUser.DoesNotExist:
                return JsonResponse(data={}, status=401)
            if user.is_active and __is_expire_token(user.date_token_renewed):
                system = {'__user': user, 'query': request.GET}
                data = request.POST
                responce, status = func(system, data)
                return JsonResponse(data=responce, status=status)
        return JsonResponse(data={}, status=401)
    return wrapped

def __parse_token(token):
    return token.split(' ')[-1]

def __is_expire_token(created_time_token):
    seconds = (timezone.now() - created_time_token).total_seconds()
    days = int(seconds // (3600*24))
    return True if days < settings.TOKEN_EXPIRE else False