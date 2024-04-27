from pathlib import Path

from django.contrib.auth.decorators import login_required
from django.core.files import File
from django.shortcuts import redirect, render

from .models import Score

import dataclasses
import json
from dataclasses import dataclass
from dataclasses import field
from .musicxml_generator import update_sheet

from django.http import HttpResponse

# Create your views here.

@dataclass
class Sheet:
    note_start_times: dict = field(default_factory=dict)
    buffer_note_start_times: dict = field(default_factory=dict)
    beat: int = 0
    measure: int = 1
    previous_note: list = field(default_factory=list) # [start_time, duration, start_beat]
    chord: bool = False
    backup: bool = False # flag for when a <backup> is used (needed to know when to place a <forward>)
    last_note_start_time: float = 0
    voice: int = 1
    dynamic: str = "unknown"
    last_dynamic: str = "unknown"
    create_measure: bool = False
    l1_note_buffer: list = field(default_factory=list)
    l2_note_buffer: list = field(default_factory=list)
    last_note_end_time: float = 0 # when the last note ends
    note_names: list = field(default_factory=list)
    bpm: int = 60
    time_sig_beats: int = 4
    

# helper fuctions
# TODO move below somewhere else
def get_note_names(key):
    note_names = {"-6": ["Cb", "C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb"],
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
                  "6": ["C", "C#", "D", "D#", "E", "E#", "F#", "G", "G#", "A", "A#", "B"]}

    return note_names[key]


def write_time_sig(time_sig_beats, path):
    with open(path, "a") as file:
        file.write("<time>\n")
        file.write(f"<beats>{time_sig_beats}</beats>\n")
        file.write("<beat-type>4</beat-type>\n")
        file.write("</time>\n")


def write_key(key, path):
    with open(path, "a") as file:
        file.write("<key>\n")
        file.write(f"<fifths>{key}</fifths>\n")
        file.write("</key>\n")


template1 = ["<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>\n", 
            "<!DOCTYPE score-partwise PUBLIC\n", 
            "\"-//Recordare//DTD MusicXML 4.0 Partwise//EN\"\n",
            "\"http://www.musicxml.org/dtds/partwise.dtd\">\n", 
            "<score-partwise version=\"4.0\">\n",
            "<part-list>\n",
            "<score-part id=\"P1\">\n",
            "<part-name>Music</part-name>\n",
            "</score-part>\n",
            "</part-list>\n",
            "<part id=\"P1\">\n",
            "<measure number=\"1\">\n",
            "<attributes>\n",
            "<divisions>8</divisions>\n"]


template2 = ["<staves>2</staves>\n",
            "<clef number=\"1\">\n",
            "<sign>G</sign>\n",
            "<line>2</line>\n",
            "</clef>\n",
            "<clef number=\"2\">\n",
            "<sign>F</sign>\n",
            "<line>4</line>\n",
            "</clef>\n"
            "</attributes>\n"]
# TODO move above somewhere else


@login_required(redirect_field_name=None)
def create_score(request):
    user_id = request.user
    username = request.user.username
    score_title = request.POST["score-title"].lower()

    filepath = Path().resolve() / "files" / username / f"{score_title}.musicxml"
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath_json = Path().resolve() / "files" / username / f"{score_title}.json"

    # django creates a copy of the file for the db
    with open(filepath, "a+") as fp:
        with open(filepath_json, "a+") as fp_json:
            score = Score(
                user=user_id,
                score_title=score_title,
                score_xml=File(fp),
                score_json=File(fp_json)
            )
            score.save()

    # delete original file
    filepath.unlink()
    filepath_json.unlink()

    sheet = Sheet()
    sheet.time_sig_beats = int(request.POST["Time Signature"])
    sheet.bpm = int(request.POST["bpm"])
    sheet.note_names = get_note_names(request.POST["key"])
    sheet.previous_note = [None, None, None]

    with open(score.score_xml.name, "a") as file:
        file.writelines(template1)
    
    write_key(request.POST["key"], score.score_xml.name)
    write_time_sig(sheet.time_sig_beats, score.score_xml.name)

    with open(score.score_xml.name, "a") as file:
        file.writelines(template2)

    with open(score.score_json.name, "w") as file:
        file.write(json.dumps(dataclasses.asdict(sheet)))

    return redirect("accounts:dashboard", username=username)


@login_required(redirect_field_name=None)
def read_score(request, slug):
    return render(request, "scores/user_page.html", {"score": Score.objects.get(user_id=request.user, score_slug=slug)})


@login_required(redirect_field_name=None)
def update_score(request, slug):
    score = Score.objects.get(user_id=request.user, score_slug=slug)
    with open(score.score_json.name, "r") as file:
        sheet = Sheet(**json.loads(file.read()))

    print(request.body)
    sheet = update_sheet(sheet, score.score_xml.name, **json.loads(request.body))

    with open(score.score_json.name, "w") as file:
        file.write(json.dumps(dataclasses.asdict(sheet)))

    return HttpResponse(status=200)


@login_required(redirect_field_name=None)
def delete_score(request, slug):
    score = Score.objects.get(user_id=request.user, score_slug=slug)
    score.delete()
    return redirect("accounts:dashboard", username=request.user.username)


@login_required(redirect_field_name=None)
def get_xml(request, slug):
    score = Score.objects.get(user_id=request.user, score_slug=slug)
    return HttpResponse(open(score.score_xml.name).read(), content_type='text/xml')