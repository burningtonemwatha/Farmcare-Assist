from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
# This view handles user account details

def home(request):
    return HttpResponse("Welcome to the Accounts Home Page")