from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.views.decorators.http import require_http_methods
from courses import models


@require_http_methods(['POST'])
@csrf_exempt
def get_document(request):
    if 'doc_id' in request.POST:
        response = models.Document.get_one(request.POST['doc_id'])
        return JsonResponse(response)
    return JsonResponse({'error': 'doc_id is undefined'})



@require_http_methods(['POST'])
@csrf_exempt
def get_folders(request):
    if 'folder_id' in request.POST:
        responce = models.Document.get_list(request.POST['folder_id'])
        return JsonResponse(responce)
    else:
        responce = list(models.Folder.objects.get_list())
        return JsonResponse(responce)