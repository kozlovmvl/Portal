from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from authentication.decorators import auth_and_parse
from .utils import ResultsFactory


@api_view(['POST'])
@csrf_exempt
@auth_and_parse
def result_statistics(system, data):
    results = ResultsFactory(**data)
    return results.data, 200

