from django.http import JsonResponse
from django.conf import settings
import secrets
from main import models

# Create your views here.
def auth(request):
    if request.type == "POST":
        try:
            token = secrets.token_hex(20)
            return JsonResponse({"code":200, "data":{"token":token}})
        except Exception:
            return JsonResponse({"code":500, "error":"Server error"})
    else:
        return JsonResponse({"code":405, "error":"Method not allowed"})
