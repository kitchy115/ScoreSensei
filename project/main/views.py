from django.shortcuts import render

# Create your views here.


def home(request):
    return render(request, 'main/home_page.html')


def login(request):
    return render(request, 'main/login_page.html')


def showcase(request):
    return render(request, 'main/user_page.html')
