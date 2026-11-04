from django.http import JsonResponse
from django.conf import settings
import secrets
from main import models
from django.contrib.auth import authenticate
import sys
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User

def write_http_error(request, error):
    print(f"An error occurred on processing request! Request metadata: ip={request.get_host()}, headers={request.headers}, method={request.method}. Error: {type(error).__name__}: {error}", file=sys.stderr)

def write_http_log(request):
    print(f"Request: method={request.method}, headers={request.headers} has processed")

def http_handler(func):
    def wrapper(request, *args, **kwargs):
        try:
            result = func(request, *args, **kwargs)
            write_http_log(request)
            return result
        except Exception as e:
            write_http_error(request, e)
            return JsonResponse({"code":500, "error":"Server error"}, status=500)

    return wrapper


# Create your views here.
@csrf_exempt
@http_handler
def auth(request):
    if request.method == "POST":
        try:
            request_data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"code":400, "error":"Bad Request"}, status=400)

        if not "data" in request_data or not isinstance(request_data["data"], dict): # Checking the 'data' key in request body
            return JsonResponse({"code":422, "error":"Unprocessable data"}, status=422)

        # Login and password getting
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
    else:
        return JsonResponse({"code":405, "error":"Method not allowed"}, status=405)

@csrf_exempt
@http_handler
def unauth(request):
    if request.method == "POST":
        try:
            request_data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"code":400, "error":"Bad Request"}, status=400)

        if "data" not in request_data or not isinstance(request_data["data"], dict):
            return JsonResponse({"code":422, "error":"Unprocessable data"}, status=422)

        target_token = request_data["data"].get("token") # Token value

        if not target_token or not isinstance(target_token, str):
            return JsonResponse({"code":422, "error":"Unprocessable data"}, status=422)

        token_object = models.Token.objects.filter(value=target_token).first() # Database object of token

        if token_object is None:
            return JsonResponse({"code":401, "error":"Unauthorized"})

        token_object.delete() # Deleting this token

        return JsonResponse({"code":200}, status=200)
    else:
        return JsonResponse({"code":405, "error":"Method not allowed"}, status=405)


@csrf_exempt
@http_handler
def profile_username(request):
    if request.method == "POST":
        try:
            request_data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"code":400, "error":"Bad Request"}, status=400)

        if "cmd" not in request_data or not isinstance(request_data["cmd"], str):
            return JsonResponse({"code":422, "error":"Unprocessable data"}, status=422)

        if request_data["cmd"] == "get":
            if "data" not in request_data or not isinstance(request_data["data"], dict):
                return JsonResponse({"code":422, "error":"Unprocessable data"}, status=422)

            token = request_data["data"].get("token")

            if not token or not isinstance(token, str):
                return JsonResponse({"code":422, "error":"Unprocessable data"}, status=422)

            token_object = models.Token.objects.filter(value=token).first()

            if token_object is None:
                return JsonResponse({"code":401, "error":"Unauthorized"}, status=401)

            user_object = token_object.user

            return JsonResponse({"code":200, "data":{"username":user_object.username}}, status=200)

        elif request_data["cmd"] == "change":

            if "data" not in request_data or not isinstance(request_data["data"], dict):
                return JsonResponse({"code":422, "error":"Unprocessable data"}, status=422)

            if "username" not in request_data["data"] or not isinstance(request_data["data"]["username"], str):
                return JsonResponse({"code":422, "error":"Unprocessable data"}, status=422)

            token = request_data["data"].get("token")

            if not token or not isinstance(token, str):
                return JsonResponse({"code":422, "error":"Unprocessable data"}, status=422)

            token_object = models.Token.objects.filter(value=token).first()

            if token_object is None:
                return JsonResponse({"code":401, "error":"Unauthorized"}, status=401)

            user_object = token_object.user

            user_object.username = request_data["data"]["username"]

            user_object.save()

            return JsonResponse({"code":200}, status=200)
    else:
        return JsonResponse({"code":405, "error":"Method not allowed"}, status=405)

@csrf_exempt
@http_handler
def write_ci_progress(request):
    if request.method == "POST":
        try:
            request_data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"code":400, "error":"Bad Request"}, status=400)

        if "data" not in request_data or not isinstance(request_data["data"], dict):
            return JsonResponse({"code":422, "error":"Unprocessable data"}, status=422)

        token = request_data["data"].get("token")
        progress = request_data["data"].get("progress")

        if not token or not isinstance(token, str):
            return JsonResponse({"code":422, "error":"Unprocessable data"}, status=422)

        if not progress or not isinstance(progress, dict):
            return JsonResponse({"code":422, "error":"Unprocessable data"}, status=422)

        money = progress.get("money")
        eggs = progress.get("eggs")
        white_eggs = progress.get("white_eggs")
        chickens = progress.get("chickens")
        vmap = progress.get("vmap") # Virtual map of the game, not usable in first versions of game with DataBase
        is_in_credit = progress.get("in_credit")
        credit_summ = progress.get("credit_summ")
        remaining_credit = progress.get("remaining_credit")
        satiety = progress.get("satiety")

        if money is None or not isinstance(money, int):
            return JsonResponse({"code":422, "error":"Unprocessable data"}, status=422)

        if eggs is None or not isinstance(eggs, int):
            return JsonResponse({"code":422, "error":"Unprocessable data"}, status=422)

        if white_eggs is None or not isinstance(white_eggs, int):
            return JsonResponse({"code":422, "error":"Unprocessable data"}, status=422)

        if chickens is None or not isinstance(chickens, list):
            return JsonResponse({"code":422, "error":"Unprocessable data"}, status=422)

        if vmap is None or not isinstance(vmap, dict):
            return JsonResponse({"code":422, "error":"Unprocessable data"}, status=422)

        if is_in_credit is None or not isinstance(is_in_credit, bool):
            return JsonResponse({"code":422, "error":"Unprocessable data"}, status=422)

        if credit_summ is None or not isinstance(credit_summ, int):
            return JsonResponse({"code":422, "error":"Unprocessable data"}, status=422)

        if remaining_credit is None or not isinstance(remaining_credit, int):
            return JsonResponse({"code":422, "error":"Unprocessable data"}, status=422)

        if satiety is None or not isinstance(satiety, int):
            return JsonResponse({"code":422, "error":"Unprocessable data"}, status=422)

        token_object = models.Token.objects.filter(value=token).first()
        if token_object is None:
            return JsonResponse({"code":401, "error":"Unauthorized"}, status=401)

        user_object = token_object.user
        id = models.Id.objects.filter(user=user_object).first()
        player = models.Chicken_Impire_Player.objects.filter(target_id=id).first()
        farm = models.CI_Farm.objects.filter(player=player).first()


        if player is None or farm is None:
            id.check_models()
            player = models.Chicken_Impire_Player.objects.filter(target_id=id).first()
            farm = models.CI_Farm.objects.filter(player=player).first()

        farm.money = money
        farm.eggs = eggs
        farm.white_eggs = white_eggs
        farm.chickens = chickens
        farm.vmap = vmap
        farm.is_in_credit = is_in_credit
        farm.credit_summ = credit_summ
        farm.remaining_credit = remaining_credit
        farm.satiety = satiety

        farm.save()

        return JsonResponse({"code":200}, status=200)
    else:
        return JsonResponse({"code":405, "error":"Method not allowed"}, status=405)


@csrf_exempt
@http_handler
def get_ci_progress(request):
    if request.method == "POST":
        try:
            request_data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"code":400, "error":"Bad request"}, status=400)

        if "data" not in request_data or not isinstance(request_data["data"], dict):
            return JsonResponse({"code":422, "error":"Unprocessable data"}, status=422)

        token = request_data["data"].get("token")

        if not token or not isinstance(token, str):
            return JsonResponse({"code":422, "error":"Unprocessable data"}, status=422)

        token_object = models.Token.objects.filter(value=token).first()

        if token_object is None:
            return JsonResponse({"code":401, "error":"Unauthorized"}, status=401)

        user_object = token_object.user

        id = models.Id.objects.filter(user=user_object).first()
        player = models.Chicken_Impire_Player.objects.filter(target_id=id).first()
        farm = models.CI_Farm.objects.filter(player=player).first()

        if player is None or farm is None:
            id.check_models()
            player = models.Chicken_Impire_Player.objects.filter(target_id=id).first()
            farm = models.CI_Farm.objects.filter(player=player).first()

        money = farm.money
        eggs = farm.eggs
        white_eggs = farm.white_eggs
        chickens = farm.chickens
        vmap = farm.vmap
        is_in_credit = farm.is_in_credit
        credit_summ = farm.credit_summ
        remaining_credit = farm.remaining_credit
        satiety = farm.satiety

        return JsonResponse({"code":200, "data":{"progress":{"money":money, "eggs":eggs, "white_eggs":white_eggs, "chickens":chickens, "vmap":vmap, "is_in_credit":is_in_credit, "credit_summ":credit_summ, "remaining_credit":remaining_credit, "satiety":satiety}}}, status=200)
    else:
        return JsonResponse({"code":405, "error":"Method not allowed"}, status=405)

@csrf_exempt
@http_handler
def signup(request):
    if request.method == "POST":
        try:
            request_data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"code":400, "error":"Bad request"}, status=400)

        if "data" not in request_data:
            return JsonResponse({"code":422, "error":"Unprocessable data"}, status=422)

        username = request_data["data"].get("username")
        password = request_data["data"].get("password")
        email = request_data["data"].get("email")

        if username is None or password is None or email is None:
            return JsonResponse({"code":422, "error":"Unprocessable data"}, status=422)

        if not isinstance(username, str) or not isinstance(password, str) or not isinstance(email, str):
            return JsonResponse({"code":422, "error":"Unprocessable data"}, status=422)

        new_user = User.objects.create_user(username=username, password=password, email=email)
        new_id = models.Id(user=new_user)
        new_id.save()
        new_id.check_models()

        token = secrets.token_hex(20)

        token_row = models.Token(user=new_user, value=token)
        token_row.save()

        return JsonResponse({"code":200, "data":{"token":token}}, status=200)
    else:
        return JsonResponse({"code":405, "error":"Method not allowed"}, status=405)
