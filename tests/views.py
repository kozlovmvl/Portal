from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from authentication.decorators import auth_and_parse
from tests import models


@api_view(['POST'])
@csrf_exempt
@auth_and_parse
def test_all(system, data):
    response = {'tests': models.Test.get_list(system['__user'])}
    return response, 200


@api_view(['POST'])
@csrf_exempt
@auth_and_parse
def test_get(system, data):
    try:
        response = models.Test.get_one(data['test_id'])
        return response, 200
    except models.Test.DoesNotExist:
        return {'error': 'object is not find'}, 404


@api_view(['POST'])
@csrf_exempt
@auth_and_parse
def attempt_start(system, data):
    attempt = models.Attempt.objects.create(
        user_id=system['__user'].id, test_id=data['test_id'])
    questions = models.Question.get_questions(data['test_id'])
    return {'attempt_id': attempt.id, 'questions': questions}, 200


@api_view(['POST'])
@csrf_exempt
@auth_and_parse
def attempt_finish(system, data):
    try:
        attempt = models.Attempt.objects.get(id=data['attempt_id'])
    except models.Attempt.DoesNotExist:
        return {'error': 'attempt_not_found'}, 404
    if attempt.is_expired():
        return {'error': 'attempt_is_expired'}, 400
    result = models.Answer.add(system['__user'], attempt, data['answers'])
    attempt.close(result)
    return result, 200
