import json

from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

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
        test = models.Test.is_exist(data['test_id'])
        if not test:
            return {}, 400
        attempt = models.Attempt.objects.create(
            user_id=system['__user'].id, test_id=data['test_id'])
        questions = models.Question.get_questions(data['test_id'])
        return {'attempt_id': attempt.id, 'questions': questions}, 200
    return {}, 400


@api_view(['POST'])
@csrf_exempt
@auth_and_parse
def attempt_finish(system, data):
    if ('attempt_id' and 'answers') in data:
        answers = json.loads(data['answers'])
        attempt = models.Attempt.is_exist(data['attempt_id'])
        if attempt is None:
            return {}, 400
        result, status = models.Answer.add(system['__user'], attempt, answers)
        return result, status
    return {}, 400
