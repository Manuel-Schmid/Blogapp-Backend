from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie


@csrf_exempt
@ensure_csrf_cookie
def set_csrf(request: WSGIRequest) -> HttpResponse:
    return HttpResponse(status=204)
