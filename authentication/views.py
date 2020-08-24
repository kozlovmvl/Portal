from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import user_logged_in, authenticate
from django.utils import timezone
from django.conf import settings
from uuid import uuid1

@require_http_methods(['POST'])
@csrf_exempt
def signin(request):
    if not request.user.is_authenticated:
        if ('username' and 'password') in request.POST:
            #если поля существуют, то ищем пользователя.
            user = authenticate(username=request.POST['username'], password=request.POST['password'])
            if user is not None:
                #переводим секунды в дни с момента последней авторизации.
                seconds = (timezone.now() - user.date_token_renewed).total_seconds()
                days = int(seconds // (3600*24))

                #сверяем дни с заданной setting переменной
                if (days >= settings.TOKEN_EXPIRE):
                    user.token = uuid1()
                    user.date_token_renewed = timezone.now()
                    user.save()
                    return JsonResponse(status=200, data={'token': user.token})
                else:
                    return JsonResponse({'token': user.token})

    return HttpResponse(status=401)