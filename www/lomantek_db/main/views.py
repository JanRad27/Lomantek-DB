from django.http import JsonResponse
from django.conf import settings
import secrets
from main import models
from django.contrib.auth import authenticate
import sys
import json
from django.views.decorators.csrf import csrf_exempt

def write_http_error(request, error):
    print(f"An error occurred on processing request! Request metadata: ip={request.get_host()}, headers={request.headers}, method={request.method}, body={request.body}. Error: {type(error).__name__}: {error}", file=sys.stderr)

# Create your views here.
@csrf_exempt
def auth(request):
    if request.method == "POST":
        try:
            try:
                request_data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({"code":400, "error":"Bad Request"}, status=400)

            if not "data" in request_data or not isinstance(request_data["data"], dict): # Checking the 'data' key in request body
                return JsonResponse({"code":422, "error":"Unprocessable data"}, status=422)

            # Login and password writing
            login = request_data["data"].get("login", None)
            password = request_data["data"].get("password", None)

            if not login or not password: # Checking the login and password
                return JsonResponse({"code":422, "error":"Unprocessable data"}, status=422)

            user = authenticate(request, username=login, password=password) # Authentificating the user

            if not user:
                return JsonResponse({"code":401, "error":"Unauthorized"}, status=401) # User not found or login/password is incorrect

            token = secrets.token_hex(20) # Generating the token

            db_row = models.Token(user=user, value=token)
            db_row.save() # Writing db

            return JsonResponse({"code":200, "data":{"token":token}}, status=200) # Okay
        except Exception as e:
            write_http_error(request, e)
            return JsonResponse({"code":500, "error":"Server error"}, status=500)
    else:
        return JsonResponse({"code":405, "error":"Method not allowed"}, status=405)

@csrf_exempt
def unauth(request):
    if request.method == "POST":
        try:
            try:
                request_data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({"code":400, "error":"Bad Request"}, status=400)

            if "data" not in request_data or not isinstance(request_data["data"], dict):
                return JsonResponse({"code":422, "error":"Unprocessable data"}, status=422)

            target_token = request_data["data"].get("token") # Token value

            if not target_token:
                return JsonResponse({"code":422, "error":"Unprocessable data"}, status=422)

            token_object = models.Token.objects.filter(value=target_token) # Database object of token

            token_object.delete() # Deleting this token

            return JsonResponse({"code":200}, status=200)

        except Exception as e:
            write_http_error(request, e)
            return JsonResponse({"code":500, "error":"Server error"}, status=500)
    else:
        return JsonResponse({"code":405, "error":"Method not allowed"}, status=405)
