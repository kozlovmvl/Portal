from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from courses import models


# TODO: везде вместо require_http_methods использовать api_view(['POST']) из rest_framework.decorators
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
        # TODO: вот так
        response = {
            'documents': models.Document.get_list(request.POST['folder_id'])
        }
        return JsonResponse(response)
    else:
        responce = list(models.Folder.objects.get_list())
        return JsonResponse(responce)