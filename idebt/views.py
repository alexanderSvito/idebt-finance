from django.http import JsonResponse


def custom404(request, exception):
    return JsonResponse({
        'status': 'error',
        'error': 'The resource was not found'
    }, status=404)


def custom500(request, *args, **kwargs):
    return JsonResponse({
        'status': 'error',
        'error': 'Server experienced internal error'
    }, status=500)

