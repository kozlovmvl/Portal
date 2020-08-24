from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view
from courses import models


@api_view(['POST'])
@csrf_exempt
def get_document(request):
    if 'doc_id' in request.POST:
        response = models.Document.get_one(request.POST['doc_id'])
        return JsonResponse(response)
    return JsonResponse({'error': 'doc_id is undefined'})


@api_view(['POST'])
@csrf_exempt
def get_folders(request):
    if 'folder_id' in request.POST:
        response = { 'documents': models.Document.get_list(request.POST['folder_id']) }
        return JsonResponse(response)
    else:
        responce = { 'folders': models.Folder.get_list() }
        return JsonResponse(responce)