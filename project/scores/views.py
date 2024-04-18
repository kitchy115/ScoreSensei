from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .models import Score

# Create your views here.


@login_required(redirect_field_name=None)
def create_score(request):
    title = request.POST["filename"]
    score = Score(user=request.user, title=title)
    score.save()
    return redirect("accounts:dashboard", username=request.user.username)


@login_required(redirect_field_name=None)
def all_scores(request):
    pass


@login_required(redirect_field_name=None)
def read_score(request, slug):
    return render(request, "scores/user_page.html")


@login_required(redirect_field_name=None)
def update_score(request, slug):
    pass


@login_required(redirect_field_name=None)
def delete_score(request, slug):
    pass
