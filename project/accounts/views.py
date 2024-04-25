from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect, render

from scores.models import Score

from .forms import RegistrationForm

# Create your views here.


def user_register_login(request):
    if not request.user.is_anonymous:
        return redirect("main:home")

    if request.POST.get("submit") == "register":
        form = RegistrationForm(request.POST)

        if form.is_valid():
            form.save()
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password1"]
            user = authenticate(username=username, password=password)

            login(request, user)
            messages.success(request, "Registration successful")
            return redirect("main:home")
    else:
        form = RegistrationForm()

    if request.POST.get("submit") == "login":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("main:home")
        else:
            messages.error(request, "You have entered an invalid username or password")
            return redirect("accounts:login")

    return render(request, "accounts/register_login_page.html", {"form": form})


def user_logout(request):
    logout(request)
    messages.success(request, "You were logged out")
    return redirect("main:home")


@login_required(redirect_field_name=None)
def dashboard(request, username):
    if username != request.user.username:
        raise Http404

    scores = Score.objects.filter(user=request.user)
    return render(request, "accounts/dashboard_page.html", {"scores": scores})
