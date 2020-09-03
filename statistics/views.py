from django.views.decorators.csrf import csrf_exempt

from authentication.decorators import auth_and_parse
from rest_framework.decorators import api_view
from tests import models


@api_view(['POST'])
@csrf_exempt
@auth_and_parse
def result_statistics(system, data):
    list_obj = None
    if ('test_id' in data) and ('user_id' in data):
        list_obj = models.Test.get_statistics_user_test(data['user_id'], data['test_id'])
    elif 'test_id' in data:
        list_obj = models.Test.get_list_statistics_for_test(data['test_id'])
    elif 'user_id' in data:
        list_obj = models.Test.get_list_statistics(users=[data['user_id']])
    else:
        list_obj = models.Test.get_list_statistics()
    if list_obj is not None:
        return {'results': list_obj}, 200
    return {'error': 'test_id is not exist'}, 200
