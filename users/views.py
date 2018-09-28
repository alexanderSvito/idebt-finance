from idebt.ajax import ajax

from users.forms import RegisterForm
from django.http import JsonResponse


@ajax(require_POST=True)
def signup(request):
    form = RegisterForm(request.POST)
    if form.is_valid():
        user = form.save()
        return JsonResponse({
            "status": "ok",
            "user": user.to_json()
        })
    else:
        return JsonResponse({
            "status": "error",
            "message": form.errors
        }, status=422)
