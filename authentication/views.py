from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from .models import CustomUser


@csrf_exempt
@api_view(['POST'])
def sign_in(request):
    try:
        user = CustomUser.objects.get(username=request.POST['username'])
    except ObjectDoesNotExist:
        return JsonResponse(status=401, data={})
    if user.is_active and user.check_password(request.POST['password']):
        token = user.create_token()
        return JsonResponse({'token': token})
    return JsonResponse(status=401, data={})
