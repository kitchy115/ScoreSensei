import pygame.midi as midi
import keyboard
import time

template = ["<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>\n",
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
            "<divisions>1</divisions>\n",
            "<key>\n",
            "<fifths>0</fifths>\n",
            "</key>\n",
            "<time>\n",
            "<beats>4</beats>\n",
            "<beat-type>4</beat-type>\n",
            "</time>\n",
            "<clef>\n",
            "<sign>G</sign>\n",
            "<line>2</line>\n",
            "</clef>\n",
            "</attributes>\n"]

template_ending = ["</measure>\n",
                   "</part>\n",
                   "</score-partwise>"]

note_template = ["<note>\n",
                 "<pitch>\n"]

note_ending = {"quarter": "</pitch>\n<duration>1</duration>\n<type>quarter</type>\n</note>\n",
               "half": "</pitch>\n<duration>2</duration>\n<type>half</type>\n</note>\n",
               "whole": "</pitch>\n<duration>4</duration>\n<type>whole</type>\n</note>\n",
               "eighth": "</pitch>\n<duration>0.5</duration>\n<type>eighth</type>\n</note>\n",
               "sixteenth": "</pitch>\n<duration>0.25</duration>\n<type>sixteenth</type>\n</note>\n",
               "thirty-second": "</pitch>\n<duration>0.125</duration>\n<type>thirty-second</type>\n</note>\n"}

midi.init()

# This prints the default device ids that we are outputting to / taking input from
print('Output ID', midi.get_default_output_id())
print('Input ID', midi.get_default_input_id())

# List the MIDI devices that can be used
for i in range(0, midi.get_count()):
    print(i, midi.get_device_info(i))

input_device = midi.Input(1)

# Calculate durations
BPM = 60
QUARTER_DURATION = 60 / BPM
HALF_DURATION = 2 * QUARTER_DURATION
WHOLE_DURATION = 4 * QUARTER_DURATION
EIGHTH_DURATION = QUARTER_DURATION / 2
SIXTEENTH_DURATION = QUARTER_DURATION / 4
THIRTY_SECOND_DURATION = QUARTER_DURATION / 8


def get_note(note_number):
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    return note_names[note_number % 12]


def get_octave(note_number):
    return (note_number // 12) - 1  # // = truncating division


def get_note_duration(start_time, end_time):
    duration = end_time - start_time
    error = .51

    if abs(WHOLE_DURATION * error <= duration <= WHOLE_DURATION / error):
        return "whole"
    elif abs(HALF_DURATION * error <= duration <= HALF_DURATION / error):
        return "half"
    elif abs(QUARTER_DURATION * error <= duration <= QUARTER_DURATION / error):
        return "quarter"
    elif abs(EIGHTH_DURATION * error <= duration <= EIGHTH_DURATION / error):
        return "eighth"
    elif abs(SIXTEENTH_DURATION * error <= duration <= SIXTEENTH_DURATION / error):
        return "sixteenth"
    elif abs(THIRTY_SECOND_DURATION * error <= duration <= THIRTY_SECOND_DURATION / error):
        return "thirty-second"
    else:
        return "unknown"

active_notes = set()  # can only be unique notes, but can also be array doesn't matter
note_start_times = {}
chord_processed = False  # flag to track whether a chord release event has been processed
beat = 0
measure = 1

DEBOUNCE_DELAY = 9 / BPM  # The higher the numerator is here, the less sensitive it is to chords. *9 seems very good btw
try:
    print('*** Ready to play ***')
    print('**Press [q] to quit**')
git 
    with open("sheet.musicxml", "w") as file:
        file.writelines(template)

    last_note_end_time = 0  # when the last note ends
    last_note_start_time = 0  # trying something out here

    while not keyboard.is_pressed('q'):
        # Detect keypress on input
        if input_device.poll():
            # Get MIDI event information
            midi_events = input_device.read(1000)

            for event in midi_events:
                data, timestamp = event[0], event[1]
                status, note, velocity, _ = data

                if status == 144 and velocity > 0:  # key pressed
                    last_note_start_time = time.time()  # time started
                    note_start_times[note] = time.time()
                    active_notes.add(note)
                    chord_processed = False  # Reset the flag when a new note is pressed

                elif (status == 128) or (status == 144 and velocity == 0):  # key released
                    if note in active_notes:
                        active_notes.remove(note)
                        start_time = note_start_times.pop(note, None)
                        end_time = time.time()
                        d = "{:.4f}".format(abs(start_time - end_time))
                        duration = get_note_duration(start_time, end_time)
                        note_name = get_note(note)
                        octave = get_octave(note)

                        # Check if consecutive notes are too close, treat them as one if so
                        if len(active_notes) > 0:
                            first_note = next(iter(active_notes))
                            time_diff = note_start_times[first_note] - last_note_end_time

                        if len(active_notes) < 1:
                            print(f"Note:{note_name}, Octave:{octave}, Duration:{duration}, Exact Duration:{d} seconds")
                            last_note_end_time = time.time()

                        if len(active_notes) >= 1:
                            print(f"Chord Duration:{duration}, Exact Duration:{d} ")
                            last_note_end_time = time.time()

                        if duration != "unknown" and not chord_processed and len(active_notes) >= 1:
                            # Generate and append MusicXML note entry
                            with open("sheet.musicxml", "a") as file:
                                file.writelines(note_template)
                                file.write(f"<step>{note_name}</step>\n")
                                if "#" in note_name:
                                    file.write("<alter>1</alter>\n")
                                file.write(f"<octave>{octave}</octave>\n")
                                file.writelines(note_ending[duration])

                            chord_processed = True  # Set the flag to indicate that the chord release has been processed
                            active_notes.clear()  # Clear active notes if it was a chord

            # Print currently active notes
            if not chord_processed and len(active_notes) > 1:  # Only print individual notes
                active_notes_str = ", ".join([get_note(note) for note in active_notes])
                active_octaves_str = ([str(get_octave(note)) for note in active_notes])
                print(f"Chord: {active_notes_str}")
                print(f"Octaves: {active_octaves_str}")



        # Debounce delay ***
        time.sleep(DEBOUNCE_DELAY)

finally:
    # Close the midi interface
    midi.quit()

    # write template_ending
    with open("sheet.musicxml", "a") as file:
        file.writelines(template_ending)

