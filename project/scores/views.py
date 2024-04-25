from pathlib import Path

from django.contrib.auth.decorators import login_required
from django.core.files import File
from django.shortcuts import redirect, render

from .models import Score

# Create your views here.


@login_required(redirect_field_name=None)
def create_score(request):
    user_id = request.user
    username = request.user.username
    score_title = request.POST["score-title"].lower()

    filepath = Path().resolve() / "files" / username / f"{score_title}.xml"
    filepath.parent.mkdir(parents=True, exist_ok=True)

    # django creates a copy of the file for the db
    with open(filepath, "a+") as fp:
        score = Score(
            user=user_id,
            score_title=score_title,
            score_xml=File(fp),
        )
        score.save()

    # delete original file
    filepath.unlink()

    return redirect("accounts:dashboard", username=username)


@login_required(redirect_field_name=None)
def read_score(request, slug):
    return render(request, "scores/user_page.html")


@login_required(redirect_field_name=None)
def update_score(request, slug):
    pass


@login_required(redirect_field_name=None)
def delete_score(request, slug):
    score = Score.objects.get(user_id=request.user, score_slug=slug)
    score.delete()
    return redirect("accounts:dashboard", username=request.user.username)
