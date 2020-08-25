from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from courses import models

from authentication.decorators import auth_and_parse

@api_view(['POST'])
@csrf_exempt
@auth_and_parse
def get_document(system, data):
    if 'doc_id' in data:
        response, status = models.Document.get_one(data['doc_id'])
        return response, status
    return {'error': 'doc_id is undefined'}, 400


@api_view(['POST'])
@csrf_exempt
@auth_and_parse
def get_folders(system, data):
    if 'folder_id' in data:
        response = { 'documents': models.Document.get_list(data['folder_id']) }
        return response, 200
    else:
        response = { 'folders': models.Folder.get_list() }
        return response, 200