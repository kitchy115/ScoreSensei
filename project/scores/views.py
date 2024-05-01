import json
import threading
from dataclasses import asdict, dataclass, field
from pathlib import Path

from django.contrib.auth.decorators import login_required
from django.core.files import File
from django.http import HttpResponse
from django.shortcuts import redirect, render

from .models import Score
from .musicxml_generator import update_sheet

# Create your views here.


@dataclass
class Sheet:
    note_start_times: dict = field(default_factory=dict)
    buffer_note_start_times: dict = field(default_factory=dict)
    beat: int = 0
    measure: int = 1
    previous_note: list = field(
        default_factory=list
    )  # [start_time, duration, start_beat]
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


lock = threading.Lock()


# helper fuctions
# TODO move below somewhere else
def get_note_names(key):
    note_names = {
        "-6": ["Cb", "C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb"],
        "-5": ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"],
        "-4": ["C", "Db", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"],
        "-3": ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"],
        "-2": ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "G#", "A", "Bb", "B"],
        "-1": ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "Bb", "B"],
        "0": ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"],
        "1": ["C", "Db", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"],
        "2": ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"],
        "3": ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "G#", "A", "Bb", "B"],
        "4": ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "Bb", "B"],
        "5": ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"],
        "6": ["C", "C#", "D", "D#", "E", "E#", "F#", "G", "G#", "A", "A#", "B"],
    }

    return note_names[key]


template1 = [
    '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n',
    "<!DOCTYPE score-partwise PUBLIC\n",
    '"-//Recordare//DTD MusicXML 4.0 Partwise//EN"\n',
    '"http://www.musicxml.org/dtds/partwise.dtd">\n',
    '<score-partwise version="4.0">\n',
    "<part-list>\n",
    '<score-part id="P1">\n',
    "<part-name>Music</part-name>\n",
    "</score-part>\n",
    "</part-list>\n",
    '<part id="P1">\n',
    '<measure number="1">\n',
    "<attributes>\n",
    "<divisions>8</divisions>\n",
]


template2 = [
    "<staves>2</staves>\n",
    '<clef number="1">\n',
    "<sign>G</sign>\n",
    "<line>2</line>\n",
    "</clef>\n",
    '<clef number="2">\n',
    "<sign>F</sign>\n",
    "<line>4</line>\n",
    "</clef>\n" "</attributes>\n",
]
# TODO move above somewhere else


@login_required(redirect_field_name=None)
def create_score(request):
    user_id = request.user
    username = request.user.username
    score_title = request.POST["score-title"].lower()

    sheet = Sheet(
        time_sig_beats=int(request.POST["Time Signature"]),
        bpm=int(request.POST["bpm"]),
        note_names=get_note_names(request.POST["key"]),
        previous_note=[None, None, None],
    )

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
        xml_fp.write(f"<beats>{sheet.time_sig_beats}</beats>\n")
        xml_fp.write("<beat-type>4</beat-type>\n")
        xml_fp.write("</time>\n")

        xml_fp.writelines(template2)

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
    score = Score.objects.get(user_id=request.user, score_slug=slug)

    while lock.locked():
        pass
    lock.acquire()
    with open(score.score_json.name, "r") as file:
        sheet = Sheet(**json.loads(file.read()))

    print(request.body)
    sheet = update_sheet(sheet, score.score_xml.name, **json.loads(request.body))

    with open(score.score_json.name, "w") as file:
        file.write(json.dumps(asdict(sheet)))
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
