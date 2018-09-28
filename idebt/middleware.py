import json

from django.http.request import QueryDict


def JsonMiddleware(get_response):
    """
    Process application/json requests data from GET and POST requests.
    """
    def middleware(request):
        if (request.META.get('CONTENT_TYPE')
                and 'application/json' in request.META['CONTENT_TYPE']):

            data = json.loads(request.body.decode())
            q_data = QueryDict('', mutable=True)
            for key, value in data.items():
                if isinstance(value, list):
                    for x in value:
                        q_data.update({key: x})
                else:
                    q_data.update({key: value})

            if request.method == 'GET':
                request.GET = q_data

            elif request.method == 'POST':
                request.POST = q_data

        response = get_response(request)

        return response

    return middleware
