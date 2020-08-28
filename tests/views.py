from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
import json

from authentication.decorators import auth_and_parse
from tests import models

@api_view(['POST'])
@csrf_exempt
@auth_and_parse
def test_all(system, data):
    response = {
        'tests': models.Test.get_list(system['__user'])
    }
    return response, 200

@api_view(['POST'])
@csrf_exempt
@auth_and_parse
def test_get(system, data):
    if 'test_id' in data and len(data['test_id']):
        response = models.Test.get_one(data['test_id'])
        return response, 200
    return {}, 400

@api_view(['POST'])
@csrf_exempt
@auth_and_parse
def attempt_start(system, data):
    if 'test_id' in data and len(data['test_id']):
        attempt, status = models.Attempt.get_test(system['__user'], data['test_id'])
        return attempt, status
    return {}, 400

@api_view(['POST'])
@csrf_exempt
@auth_and_parse
def attempt_finish(system, data):
    if ('attempt_id' and 'answers') in data:
        answers = json.loads(data['answers'])
        result, status = models.Answer.get_result(system['__user'], data['attempt_id'], answers)
        return result, status
    return {}, 400
