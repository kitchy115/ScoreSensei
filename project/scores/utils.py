# helper fuctions
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
