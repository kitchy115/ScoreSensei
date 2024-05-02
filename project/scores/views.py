import json
import threading
from time import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

from django.contrib.auth.decorators import login_required
from django.core.files import File
from django.http import FileResponse, HttpResponse
from django.shortcuts import redirect, render

from .models import Score
from .musicxml_generator import update_sheet
from .utils import get_note_names, template1, template2

# Create your views here.


@dataclass
class Sheet:
    note_start_times: dict = field(default_factory=dict)
    buffer_note_start_times: dict = field(default_factory=dict)
    beat: int = 0
    measure: int = 1
    previous_note: list = field(
        default_factory=list
    )  # [start_time, start_beat, tied]
    chord: bool = False
    backup: bool = False  # flag for when a <backup> is used (needed to know when to place a <forward>)
    last_note_start_time: float = 0
    voice: int = 1
    dynamic: str = "unknown"
    last_dynamic: str = "unknown"
    create_measure: bool = False
    l1_note_buffer: list = field(default_factory=list)
    l2_note_buffer: list = field(default_factory=list)
    last_note_end_time: float = 0  # when the last note ends
    note_names: list = field(default_factory=list)
    bpm: int = 60
    time_sig_beats: int = 4
    pedal_pressed: bool = False
    notes_during_pedal: bool = False
    pedal_markup_buffer: list = field(default_factory=list)
    after_backup_beat: int = 0


lock = threading.Lock()


@login_required(redirect_field_name=None)
def create_score(request):
    user_id = request.user
    username = request.user.username
    score_title = request.POST["score-title"].lower()

    BASE_DIR = Path().resolve() / "files" / username
    BASE_DIR.mkdir(parents=True, exist_ok=True)

    xml_path = BASE_DIR / f"{score_title}.musicxml"
    json_path = BASE_DIR / f"{score_title}.json"

    # django creates a copy of the file for the db
    with open(xml_path, "w+") as xml_fp, open(json_path, "w+") as json_fp:
        xml_fp.writelines(template1)

        xml_fp.write("<key>\n")
        xml_fp.write(f"<fifths>{request.POST['key']}</fifths>\n")
        xml_fp.write("</key>\n")

        xml_fp.write("<time>\n")
        xml_fp.write(f"<beats>{request.POST['Time Signature']}</beats>\n")
        xml_fp.write("<beat-type>4</beat-type>\n")
        xml_fp.write("</time>\n")

        xml_fp.writelines(template2)

        sheet = Sheet(
            time_sig_beats=int(request.POST["Time Signature"]),
            bpm=int(request.POST["bpm"]),
            note_names=get_note_names(request.POST["key"]),
            previous_note=[None, None, None],
        )
        json_fp.write(json.dumps(asdict(sheet)))

        score = Score(
            user=user_id,
            score_title=score_title,
            score_xml=File(xml_fp),
            score_json=File(json_fp),
        )
        score.save()

    # delete original file
    xml_path.unlink()
    json_path.unlink()

    return redirect("accounts:dashboard", username=username)


@login_required(redirect_field_name=None)
def read_score(request, slug):
    score = Score.objects.get(user_id=request.user, score_slug=slug)
    return render(request, "scores/user_page.html", {"score": score})


@login_required(redirect_field_name=None)
def update_score(request, slug):
    while lock.locked():
        pass

    lock.acquire()
    score = Score.objects.get(user_id=request.user, score_slug=slug)

    with open(score.score_json.name, "r+") as json_fp:
        sheet = Sheet(**json.loads(json_fp.read()))
        sheet = update_sheet(sheet, score.score_xml.name, **json.loads(request.body))

        json_fp.seek(0)
        json_fp.write(json.dumps(asdict(sheet)))
        json_fp.truncate()

    lock.release()

    return HttpResponse(status=200)


@login_required(redirect_field_name=None)
def delete_score(request, slug):
    score = Score.objects.get(user_id=request.user, score_slug=slug)
    score.delete()
    return redirect("accounts:dashboard", username=request.user.username)


@login_required(redirect_field_name=None)
def get_xml(request, slug):
    score = Score.objects.get(user_id=request.user, score_slug=slug)
    return HttpResponse(open(score.score_xml.name).read(), content_type="text/xml")


@login_required(redirect_field_name=None)
def download_score(request, slug):
    score = Score.objects.get(user_id=request.user, score_slug=slug)
    xml_fp = open(score.score_xml.name, "rb")
    return FileResponse(xml_fp, filename=f"{score.score_slug}.musicxml")