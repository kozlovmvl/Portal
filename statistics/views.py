from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from authentication.decorators import auth_and_parse
from tests import models


@api_view(['POST'])
@csrf_exempt
@auth_and_parse
def result_statistics(system, data):
    list_obj = None
    if ('test_id' in data) and ('user_id' in data) :
        list_obj = models.Attempt.get_list(user_id=data['user_id'], test_id=data['test_id'])
    elif 'test_id' in data:
        list_obj = models.Attempt.get_list(test_id=data['test_id'])
    elif 'user_id' in data:
        list_obj = models.Attempt.get_list(user_id=data['user_id'])
    else:
        list_obj = models.Attempt.get_list()
    if list_obj is not None:
        return {'results': list_obj}, 200
    return {'error': 'test_id is not exist'}, 200
