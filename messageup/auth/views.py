from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
def login_view(request):
    return HttpResponse("Login Page")

def register_view(request):
    return HttpResponse("Register Page")

