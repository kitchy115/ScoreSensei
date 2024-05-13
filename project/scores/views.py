import json
import threading
from dataclasses import asdict, dataclass, field
from pathlib import Path
from time import sleep

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
    )  # [start_time, duration, dotted, voice, start_beat]
    chord: bool = False
    backup: bool = False  # flag for when a <backup> is used
    last_note_start_time: float = 0
    # voice: int = 1
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
    after_backup_beat: int = 32
    backup_voice: int = 1


note_list = []

condition = threading.Condition()
modified = False


@login_required(redirect_field_name=None)
def create_score(request):
    user_id = request.user
    username = request.user.username
    score_title = request.POST["score-title"].lower()

    xml_path = Path(f"{score_title}.musicxml")
    json_path = Path(f"{score_title}.json")

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
            previous_note=[None, None, None, None],
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
    event = json.loads(request.body)["event"]
    if event[0] == 144:
        event[3] += 0.05
        sleep(0.05)  # wait for any off_notes
    note_list.append(event)
    
    with condition:

        
        print(f"Post Append: {note_list}")
        event = min(note_list, key=lambda event: event[3])  # return smallest event_time
        note_list.pop(
            note_list.index(event)
        )  # remove smallest event_time from note_list
        print(f"After pop: {note_list}")
        print(f"{event} Entering musicxml generator..")

        score = Score.objects.get(user_id=request.user, score_slug=slug)

        with open(score.score_json.path, "r+") as json_fp:
            sheet = Sheet(**json.loads(json_fp.read()))
            sheet = update_sheet(sheet, score.score_xml.path, event)

            json_fp.seek(0)
            json_fp.write(json.dumps(asdict(sheet)))
            json_fp.truncate()

        global modified

        modified = True
        condition.notify()

    return HttpResponse(status=200)


@login_required(redirect_field_name=None)
def delete_score(request, slug):
    score = Score.objects.get(user_id=request.user, score_slug=slug)
    score.delete()
    return redirect("accounts:dashboard", username=request.user.username)


@login_required(redirect_field_name=None)
def get_xml(request, slug):
    with condition:
        global modified
        while not modified:
            condition.wait()

        score = Score.objects.get(user_id=request.user, score_slug=slug)

        modified = False

    return HttpResponse(open(score.score_xml.path).read(), content_type="text/xml")


@login_required(redirect_field_name=None)
def download_score(request, slug):
    score = Score.objects.get(user_id=request.user, score_slug=slug)
    xml_fp = open(score.score_xml.path, "rb")
    return FileResponse(xml_fp, filename=f"{score.score_slug}.musicxml")
