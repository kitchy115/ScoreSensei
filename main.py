from pygame import midi
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
            "<divisions>8</divisions>\n",
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

note_to_value = {"quarter": 8,
                 "half": 16,
                 "whole": 32,
                 "eighth": 4,
                 "16th": 2,
                 "32nd": 1}

value_to_note = {8: "quarter",
                 16: "half",
                 32: "whole",
                 4: "eighth",
                 2: "16th",
                 1: "32nd"}

midi.init()

# # This prints the default device ids that we are outputting to / taking input from
# print('Output ID', midi.get_default_output_id())
# print('Input ID', midi.get_default_input_id())

# # List the MIDI devices that can be used
# for i in range(0, midi.get_count()):
#     print(i, midi.get_device_info(i))

input_device = midi.Input(midi.get_default_input_id())

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
    return (note_number // 12) - 1 # // = truncating division

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
        return "16th"
    elif abs(THIRTY_SECOND_DURATION * error <= duration <= THIRTY_SECOND_DURATION / error):
        return "32nd"
    else:
        return "unknown"

# only works in 4/4
def calc_dotted(duration):
    if duration - 32 > 0:
        return 32
    elif duration - 16 > 0:
        return 16
    elif duration - 8 > 0:
        return 8
    elif duration - 4 > 0:
        return 4
    elif duration - 2 > 0:
        return 2
    elif duration - 1 > 0:
        return 1
    else:
        return 0
    
def generate(beat, measure, duration, note_name, octave):
    # Generate and append MusicXML note entry
    with open("sheet.musicxml", "a") as file:
        # determine beats in measure
        # if beat of note is > beat remaning in measure
        # use tied note, in first measure leave beat measure needs to be comeplete
        # put remainder of note in other measure
        # i.e. measure one has 3 beats, user plays a half note
        # leave quater note in measure 1, create measure two
        # tie last note in measure 1 to left over beat (one quarter note) in measure 2
        if beat + note_to_value[duration] > 32:
            # add what can fit from this note into the measure
            file.writelines(note_template)
            file.write(f"<step>{note_name}</step>\n")
            if "#" in note_name:
                file.write("<alter>1</alter>\n")
            file.write(f"<octave>{octave}</octave>\n")
            file.write("</pitch>\n")
            if 32-beat not in value_to_note: # must use dotted note
                file.write(f"<duration>{32-beat}</duration>\n")
                file.write(f"<type>{value_to_note[calc_dotted(32-beat)]}</type>\n")
                file.write("<dot/>\n")
                file.write("<notations>\n")
                file.write("<tied type=\"start\"/>\n")
                file.write("</notations>\n")
                file.write("</note>\n")
            else:
                file.write(f"<duration>{32-beat}</duration>\n")
                file.write(f"<type>{value_to_note[32-beat]}</type>\n")
                file.write("<notations>\n")
                file.write("<tied type=\"start\"/>\n")
                file.write("</notations>\n")
                file.write("</note>\n")
            file.write("</measure>\n")
            measure += 1
            # create new measure
            file.write(f"<measure number=\"{measure}\">\n")
            file.writelines(note_template)
            file.write(f"<step>{note_name}</step>\n")
            if "#" in note_name:
                file.write("<alter>1</alter>\n")
            file.write(f"<octave>{octave}</octave>\n")
            file.write("</pitch>\n")
            # add other part of note to new measure
            if note_to_value[duration] - (32-beat) not in value_to_note: # must use dotted note
                file.write(f"<duration>{note_to_value[duration] - (32-beat)}</duration>\n")
                file.write(f"<type>{value_to_note[calc_dotted(note_to_value[duration] - (32-beat))]}</type>\n")
                file.write("<dot/>\n")
                file.write("<notations>\n")
                file.write("<tied type=\"stop\"/>\n")
                file.write("</notations>\n")
                file.write("</note>\n")
            else:
                file.write(f"<duration>{note_to_value[duration] - (32-beat)}</duration>\n")
                file.write(f"<type>{value_to_note[note_to_value[duration] - (32-beat)]}</type>\n")
                file.write("<notations>\n")
                file.write("<tied type=\"stop\"/>\n")
                file.write("</notations>\n")
                file.write("</note>\n")
            beat = note_to_value[duration] - (32-beat)
        elif beat + note_to_value[duration] == 32:
            file.writelines(note_template)
            file.write(f"<step>{note_name}</step>\n")
            if "#" in note_name:
                file.write("<alter>1</alter>\n")
            file.write(f"<octave>{octave}</octave>\n")
            file.write("</pitch>\n")
            file.write(f"<duration>{note_to_value[duration]}</duration>\n")
            file.write(f"<type>{duration}</type>\n")
            file.write("</note>\n")
            file.write("</measure>\n")
            measure += 1
            beat = 0
            file.write(f"<measure number=\"{measure}\">\n")
        else:
            file.writelines(note_template)
            file.write(f"<step>{note_name}</step>\n")
            if "#" in note_name:
                file.write("<alter>1</alter>\n")
            file.write(f"<octave>{octave}</octave>\n")
            file.write("</pitch>\n")
            file.write(f"<duration>{note_to_value[duration]}</duration>\n")
            file.write(f"<type>{duration}</type>\n")
            file.write("</note>\n")
            beat += note_to_value[duration]

    return beat, measure

note_start_times = {}
beat = 0
measure = 1

try:
    print('*** Ready to play ***')
    print('**Press [q] to quit**')

    with open("sheet.musicxml", "w") as file:
        file.writelines(template)

    while not keyboard.is_pressed('q'):
        # Detect keypress on input
        if input_device.poll():
            # Get MIDI even information
            midi_events = input_device.read(1000)
            
            for event in midi_events:
                data, timestamp = event[0], event[1]
                status, note, velocity, _ = data

                if status == 144 and velocity > 0:  # key pressed
                    note_start_times[note] = time.time()
                elif (status == 128) or (status == 144 and velocity == 0):  # key released
                    if note in note_start_times:
                        start_time = note_start_times.pop(note, None)
                        end_time = time.time()
                        d = abs(start_time-end_time)
                        duration = get_note_duration(start_time, end_time)
                        note_name = get_note(note)
                        octave = get_octave(note)

                        print(f"{note_name}{octave} {duration} {d}")

                        if duration != "unknown":
                            beat, measure = generate(beat, measure, duration, note_name, octave)
                            print(f"beat: {beat} measure: {measure}")
                        
finally:
    # Close the midi interface
    midi.quit()

    # write template_ending 
    with open("sheet.musicxml", "a") as file:
        file.writelines(template_ending)