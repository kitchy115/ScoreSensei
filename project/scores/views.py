from pathlib import Path

from django.contrib.auth.decorators import login_required
from django.core.files import File
from django.shortcuts import redirect, render

from .models import Score

import dataclasses
import json
from dataclasses import dataclass
from .musicxml_generator import update_sheet

# Create your views here.

@dataclass
class Sheet:
    note_start_times = {}
    buffer_note_start_times = {}
    beat = 0
    measure = 1
    previous_note = (None, None, None) # (start_time, duration, start_beat)
    chord = False
    backup = False # flag for when a <backup> is used (needed to know when to place a <forward>)
    last_note_start_time = 0
    voice = 1
    dynamic = None
    last_dynamic = None
    create_measure = False
    l1_note_buffer = []
    l2_note_buffer = []
    last_note_end_time = 0 # when the last note ends
    note_names = []
    bpm = 60
    time_sig_beats = 4


# helper fuctions
# TODO move below somewhere else
def get_note_names(key):
    note_names = {-6: ["Cb", "C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb"],
                  -5: ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"],
                  -4: ["C", "Db", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"],
                  -3: ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"],
                  -2: ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "G#", "A", "Bb", "B"],
                  -1: ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "Bb", "B"],
                  0: ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"],
                  1: ["C", "Db", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"],
                  2: ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"],
                  3: ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "G#", "A", "Bb", "B"],
                  4: ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "Bb", "B"],
                  5: ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"],
                  6: ["C", "C#", "D", "D#", "E", "E#", "F#", "G", "G#", "A", "A#", "B"]}

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

    sheet = Sheet()
    # sheet.time_sig_beats = time_sig_beats
    sheet.time_sig_beats = 4
    # sheet.bpm = bpm
    sheet.bpm = 60
    # sheet.note_names = get_note_names(key)
    sheet.note_names = get_note_names(0)

    # with open(score.get_absolute_url(), "a") as file:
        # file.writelines(template1)
    
    #write_key(sheet.key, score.get_absolute_url())
    #write_time_sig(sheet.time_sig_beats, score.get_absolute_url())

    #with open(score.get_absolute_url(), "a") as file:
        #file.writelines(template2)

    # json.dumps(dataclasses.asdict(sheet))

    return redirect("accounts:dashboard", username=username)


@login_required(redirect_field_name=None)
def read_score(request, slug):
    return render(request, "scores/user_page.html")


@login_required(redirect_field_name=None)
def update_score(request, slug):
    score = Score.objects.get(user_id=request.user, score_slug=slug)
    # sheet = Sheet(**json.loads(score.get_absolute_url()))



    # sheet = update_sheet(sheet, score.get_absolute_url(), event)



    # json.dumps(dataclasses.asdict(sheet))


@login_required(redirect_field_name=None)
def delete_score(request, slug):
    score = Score.objects.get(user_id=request.user, score_slug=slug)
    score.delete()
    return redirect("accounts:dashboard", username=request.user.username)
