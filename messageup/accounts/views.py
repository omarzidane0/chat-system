import email
import re

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse
from django.db import IntegrityError, transaction
from .models import Account, password_reset
from django.conf import settings 
from datetime import datetime, timedelta, timezone
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
import json
import jwt
import uuid


def password_validator(password):
    # Check length
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."

    # Check for uppercase letter
    if not any(char.isupper() for char in password):
        return False, "Password must contain at least one uppercase letter."

    # Check for lowercase letter
    if not any(char.islower() for char in password):
        return False, "Password must contain at least one lowercase letter."

    # Check for digit
    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one digit."

    # Check for special character
    special_characters = "!@#$%^&*()-_=+[]{}|;:'\",.<>?/`~"
    if not any(char in special_characters for char in password):
        return False, "Password must contain at least one special character."

    return True, "Password is valid."

def email_validator(email):
    pattern = r'^[\w.-]+@[\w.-]+\.[a-zA-Z]{2,}$'

    if re.match(pattern, email):
        return True, "Email is valid."

    return False, "Invalid email address."
# Create your views here.
@csrf_exempt
def login_view(request):
    return render(request, 'login.html')
@csrf_exempt
def login(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        username = data.get('username').strip()
        password = data.get('password').strip()
        print("Username:", username)
        if not username or not password:
            return JsonResponse({'error': 'Username and password are required.'}, status=400)
        try:
            account = Account.objects.get(username=username)
        except Account.DoesNotExist:
            return JsonResponse({'error': 'Invalid username or password.'}, status=401)
        if not check_password(password, account.password):
            return JsonResponse({'error': 'Invalid username or password.'}, status=401)
        jwt_payload = {
            'id': account.id,
            'username': account.username,
            'email': account.email,
            'iat': timezone.now(),
            'exp': timezone.now() + timedelta(hours=1)
        }
        token = jwt.encode(jwt_payload, settings.SECRET_KEY, algorithm='HS256')
        response = JsonResponse({'message': 'Login successful.', 'username': username , 'href': '/'}, status=200)
        response.set_cookie('jwt_token', token, httponly=True, secure=not settings.DEBUG, samesite='Strict')
        return response

def logout_view(request):
    if request.method == 'POST':
        response = redirect('login')
        response.delete_cookie('jwt_token', samesite='Strict')
        return response
    return redirect('login')

@csrf_exempt
def register_view(request):
    return render(request, 'register.html')

@csrf_exempt
def register(request):
        if request.method == 'POST':
            data = json.loads(request.body.decode('utf-8'))
            username = data.get('username').strip()
            password = data.get('password').strip()
            email = data.get('email').strip()
            print("Username:", username)
            if not username or not password or not email:
                return JsonResponse({'error': 'Username, password, and email are required.'}, status=400)
            if len(username) < 3:
                return JsonResponse({'error': 'Username must be at least 3 characters long.'}, status=400)
            elif len(username) > 150:
                return JsonResponse({'error': 'Username must be at most 150 characters long.'}, status=400)
            valid, message = email_validator(email)
            if not valid:
               return JsonResponse({'error': message}, status=400)
            if not password_validator(password)[0]:
                return JsonResponse({'error': password_validator(password)[1]}, status=400)
            password_h = make_password(password)
            #save the account to the database here
            try:

                with transaction.atomic():
                    account = Account.objects.create(
                        username=username,
                        email=email,
                        password=password_h,
                    )
            except IntegrityError:

                return JsonResponse(
                    {'error': 'Username or email already exists.'},
                    status=409
                ) 
            return JsonResponse({'message': 'User registered successfully.', 'username': username, 'password_hash': password_h}, status=201)
    
def forgot_password_view(request):

    if request.method == 'GET':
        return render(request, 'forgotpassword.html')
    elif request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        email = data.get('email').strip()
        if not email:
            return JsonResponse({'error': 'Email is required.'}, status=400)
        valid, message = email_validator(email)
        if not valid:
            return JsonResponse({'error': message}, status=400)
        try:
            account = Account.objects.get(email=email)
        except Account.DoesNotExist:
            return JsonResponse({'error': 'if there is an email we will send u the reset link'}, status=404)

        passwordt = password_reset.objects.filter(email=email).first()
        if passwordt:
            if timezone.now() - passwordt.created_at <= timedelta(minutes=3):
                return JsonResponse({'error': 'A reset link has already been sent. Please check your email.'}, status=429)
            elif timezone.now() - passwordt.created_at > timedelta(minutes=3):
                passwordt.delete()

        # Here you would typically send a password reset email with a token
        # For simplicity, we'll just return a success message
        reset_token = str(uuid.uuid4())
        password_reset.objects.create(email=email, reset_token=reset_token)
        send_mail(
            subject="Password Reset Request",
            message=f"Hello! You have requested a password reset. Please click the link below to reset your password: {request.build_absolute_uri(f'/reset-password/{reset_token}/')}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        return JsonResponse({'message': 'check your email for the reset link'}, status=200)

def reset_password_view(request, token):
    if request.method == 'GET':
        if not token:
            return redirect('login')
        password_resettoken = password_reset.objects.filter(reset_token=token).first()
        if not password_resettoken:
            return redirect('login')
        if timezone.now() - password_resettoken.created_at > timedelta(minutes=3):
            password_resettoken.delete()
            return redirect('login')
        return render(request, 'resetpassword.html', {'token': token})
    elif request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        new_password = data.get('new_password').strip()
        confirm_password = data.get('confirm_password').strip()
        reset_entry = password_reset.objects.filter(reset_token=token)
        if not reset_entry.exists():
            return JsonResponse({'error': 'Invalid or expired reset token.'}, status=400)
        else:
            reset_entry = reset_entry.first()
        if timezone.now() - reset_entry.created_at > timedelta(minutes=3):
            reset_entry.delete()
            return JsonResponse({'error': 'Reset token has expired.' , 'href': '/login/'}, status=400)
        if not new_password:
            return JsonResponse({'error': 'New password is required.'}, status=400)
        if not password_validator(new_password)[0]:
            return JsonResponse({'error': password_validator(new_password)[1]}, status=400)
        
        try:
            account = Account.objects.get(email=reset_entry.email)
            account.password = make_password(new_password)
            account.save()
            print("heree"+new_password)
            reset_entry.delete()  # Remove the used reset token
            return JsonResponse({'message': 'Password has been reset successfully.'}, status=200)
        except password_reset.DoesNotExist:
            return JsonResponse({'error': 'Invalid or expired reset token.'}, status=400)
        except Account.DoesNotExist:
            return JsonResponse({'error': 'Account associated with this token does not exist.'}, status=404)