from pygame import midi
import keyboard
import time

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

template_ending = ["</measure>\n",
                   "</part>\n",
                    "</score-partwise>"]

note_template = ["<note>\n",
                 "<pitch>\n"]

n_to_v = {"quarter": 8,
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

v_to_n = {8: "quarter",
          16: "half",
          32: "whole",
          4: "eighth",
          2: "16th",
          1: "32nd"}

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
    return (note_number // 12) - 1 # // = truncating division

def get_note_duration(start_time, end_time):
    duration = end_time - start_time

    if abs(WHOLE_DURATION - (WHOLE_DURATION - (HALF_DURATION + QUARTER_DURATION)) / 2 < duration):
        return "whole", False
    elif abs((HALF_DURATION + QUARTER_DURATION) - ((HALF_DURATION + QUARTER_DURATION) - HALF_DURATION) / 2 < duration):
        return "half", True
    elif abs(HALF_DURATION - (HALF_DURATION - (QUARTER_DURATION + EIGHTH_DURATION)) / 2 < duration):
        return "half", False
    elif abs((QUARTER_DURATION + EIGHTH_DURATION) - ((QUARTER_DURATION + EIGHTH_DURATION) - QUARTER_DURATION) / 2 < duration):
        return "quarter", True
    elif abs(QUARTER_DURATION - (QUARTER_DURATION - (EIGHTH_DURATION + SIXTEENTH_DURATION)) / 2 < duration):
        return "quarter", False
    elif abs((EIGHTH_DURATION + SIXTEENTH_DURATION) - ((EIGHTH_DURATION + SIXTEENTH_DURATION) - EIGHTH_DURATION) / 2 < duration):
        return "eighth", True
    elif abs(EIGHTH_DURATION - (EIGHTH_DURATION - (SIXTEENTH_DURATION + THIRTY_SECOND_DURATION)) / 2 < duration):
        return "eighth", False
    elif abs((SIXTEENTH_DURATION + THIRTY_SECOND_DURATION) - ((SIXTEENTH_DURATION + THIRTY_SECOND_DURATION) - SIXTEENTH_DURATION) / 2 < duration):
        return "16th", True
    elif abs(SIXTEENTH_DURATION - (SIXTEENTH_DURATION - (THIRTY_SECOND_DURATION + THIRTY_SECOND_DURATION / 2)) / 2 < duration):
        return "16th", False
    elif abs((THIRTY_SECOND_DURATION + THIRTY_SECOND_DURATION / 2) - ((THIRTY_SECOND_DURATION + THIRTY_SECOND_DURATION / 2) - THIRTY_SECOND_DURATION) / 2 < duration):
        return "32nd", True
    elif abs(THIRTY_SECOND_DURATION < duration):
        return "32nd", False
    else:
        return "unknown", False

# only works in 4/4
def calc_dotted(duration):
    if duration - 32 > 0: # dotted whole
        return 32
    elif duration - 16 > 0: # dotted half
        return 16
    elif duration - 8 > 0: # dotted quarter
        return 8
    elif duration - 4 > 0: # dotted eighth
        return 4
    elif duration - 2 > 0: # dotted 16th
        return 2
    elif duration - 1 > 0: # dotted 32nd
        return 1
    else:
        return 0
    
def check_dotted(duration):
    if duration == 48: # dotted whole
        return 32
    elif duration == 24: # dotted half
        return 16
    elif duration == 12: # dotted quarter
        return 8
    elif duration == 6: # dotted eighth
        return 4
    elif duration == 3: # dotted 16th
        return 2
    elif duration == 1.5: # dotted 32nd
        return 1
    else:
        return 0
    
def get_closest_note(duration):
    if duration - 48 > 0: # dotted whole
        return 48
    elif duration - 32 > 0: # whole
        return 32
    elif duration - 24 > 0:
        return 24
    elif duration - 16 > 0:
        return 16
    elif duration - 12 > 0:
        return 12
    elif duration - 8 > 0:
        return 8
    elif duration - 6 > 0:
        return 6
    elif duration - 4 > 0:
        return 4
    elif duration - 3 > 0:
        return 3
    elif duration - 2 > 0:
        return 2
    elif duration - 1.5 > 0:
        return 1.5
    elif duration - 1 > 0:
        return 1
    else:
        return 0
    
def get_dynamic(velocity):
    if velocity <= 29:
        return "ppp"
    elif velocity <= 39:
        return "pp"
    elif velocity <= 49:
        return "p"
    elif velocity <= 59:
        return "mp"
    elif velocity <= 69:
        return "mf"
    elif velocity <= 79:
        return "f"
    elif velocity <= 89:
        return "ff"
    elif 90 <= velocity:
        return "fff"
    
def note_to_value(duration, dotted):
    result = n_to_v[duration]
    if dotted == True:
        result = result + n_to_v[duration] / 2
    return result

def get_staff(note, octave):
    if octave > 4: # greater than C4
        return 1
    
    if octave == 4:
        match note:
            case "A":
                return 2 # less than C4
            case "A#":
                return 2 # less than C4
            case "B":
                return 2 # less than C4
            case "B#":
                return 2 # less than C4
            case _:
                return 1 # C4 or greater
    return 2 # less than C4

def write_backup(beat):
    with open("sheet.musicxml", "a") as file:
        file.write("<backup>\n")
        file.write(f"<duration>{beat}</duration>\n")
        file.write("</backup>\n")

def write_forward(beat):
    with open("sheet.musicxml", "a") as file:
        file.write("<foward>\n")
        file.write(f"<duration>{beat}</duration>\n")
        file.write("</foward>\n")

def write_time_sig(time_sig_beats):
    with open("sheet.musicxml", "a") as file:
        file.write("<time>\n")
        file.write(f"<beats>{time_sig_beats}</beats>\n")
        file.write("<beat-type>4</beat-type>\n")
        file.write("</time>\n")

def write_key(key):
    with open("sheet.musicxml", "a") as file:
        file.write("<key>\n")
        file.write(f"<fifths>{key}</fifths>\n")
        file.write("</key>\n")

def generate_dynamic(dynamic, staff):
    # Generate and append MusicXML note entry
    with open("sheet.musicxml", "a") as file:
        if staff == 1:
            file.write("<direction placement=\"below\">\n")
        else:
            file.write("<direction placement=\"above\">\n")
        file.write("<direction-type>\n")
        file.write("<dynamics>\n")
        file.write(f"<{dynamic}/>\n")
        file.write("</dynamics>\n")
        file.write("</direction-type>\n")
        file.write(f"<staff>{staff}</staff>\n")
        file.write("</direction>\n")
    
def generate_note(beat, measure, duration, note_name, octave, chord, voice, dotted, staff):
    # Generate and append MusicXML note entry
    with open("sheet.musicxml", "a") as file:
        file.write("<note>\n")
        if chord == True:
            file.write("<chord/>\n")
        file.write("<pitch>\n")
        file.write(f"<step>{note_name}</step>\n")
        if "#" in note_name:
            file.write("<alter>1</alter>\n")
        file.write(f"<octave>{octave}</octave>\n")
        file.write("</pitch>\n")
        file.write(f"<duration>{note_to_value(duration, dotted)}</duration>\n")
        file.write(f"<voice>{voice}</voice>\n")
        file.write(f"<type>{duration}</type>\n")
        if dotted == True:
            file.write(f"<dot/>\n")
        file.write(f"<staff>{staff}</staff>\n")
        file.write("</note>\n")
        beat += note_to_value(duration, dotted)

    return beat, measure

def generate_rest(beat, measure, duration, dotted):
    # Generate and append MusicXML note entry
    with open("sheet.musicxml", "a") as file:
        # TODO add staff support
        file.write("<note>\n")
        file.write("<rest/>\n")
        file.write(f"<duration>{note_to_value(duration, dotted)}</duration>\n")
        file.write(f"<type>{duration}</type>\n")
        if dotted == True:
            file.write(f"<dot/>\n")
        file.write("</note>\n")
        beat += note_to_value(duration, dotted)

    return beat, measure

# main(midi_note, file_name)
def main():
    note_start_times = {}
    beat = 0
    measure = 1
    previous_note = (None, None, None) # (start_time, duration, start_beat)
    chord = False
    backup = False # flag for when a <backup> is used (needed to know when to place a <forward>)
    last_note_start_time = 0
    voice = 1
    key = 0
    time_sig_beats = 4
    dynamic = None
    last_dynamic = None

    try:
        print('*** Ready to play ***')
        print('**Press [q] to quit**')

        with open("sheet.musicxml", "w") as file:
            file.writelines(template1)

        write_key(key)
        write_time_sig(time_sig_beats)
        
        with open("sheet.musicxml", "a") as file:
            file.writelines(template2)

        last_note_end_time = 0 # when the last note ends

        while not keyboard.is_pressed('`'):
            # Detect keypress on input
            if input_device.poll():
                # Get MIDI even information
                midi_events = input_device.read(1000)
                
                for event in midi_events:
                    print(event)
                    data, timestamp = event[0], event[1]
                    status, note, velocity, _ = data

                    if status == 144 and velocity > 0:  # key pressed
                        # starts at 0, then gets updated IN the loop
                        note_start_times[note] = (time.time(), beat) # record start time and amount of beats in measure (used by <backup>)
                        dynamic = get_dynamic(velocity)
                        print(f"Start time: {note_start_times[note][0]}, Start beat: {note_start_times[note][1]}, Dynamic: {dynamic}, Velocity: {velocity}")
                        #rest is calculated by the current notes start time - the last notes end time

                        # prevent chords from cloning rests, might need to tweak -0.06
                        if (last_note_end_time != 0 or last_note_start_time != 0) and last_note_start_time - note_start_times[note][0] < -0.06: #if this is not there, then it prints 0 when there is no rest
                            if backup == True:
                                backup = False
                                voice = 1
                            if chord == True:
                                chord = False

                            # use the more recent number to generate a rest
                            if last_note_start_time < last_note_end_time:
                                d = "{:.4f}".format(note_start_times[note][0] - last_note_end_time)
                                duration, dotted = get_note_duration(last_note_end_time, note_start_times[note][0])
                            else:
                                d = "{:.4f}".format(note_start_times[note][0] - last_note_start_time)
                                duration, dotted = get_note_duration(last_note_start_time, note_start_times[note][0])

                            print(f"Rest Time: {duration}, Dotted: {dotted}, Exact Duration: {d} seconds")

                            if duration != "unknown":
                                beat, measure = generate_rest(beat, measure, duration, dotted)
                                note_start_times[note] = (note_start_times[note][0], beat) # update starting beat for note
                                print(f"Updated start beat: {note_start_times[note][1]}")
                        
                        last_note_start_time = note_start_times[note][0] # record start time for next note

                    elif (status == 128) or (status == 144 and velocity == 0):  # key released
                        if note in note_start_times:
                            start_time, start_beat = note_start_times.pop(note, None)
                            end_time = time.time()
                            d = "{:.4f}".format(abs(start_time-end_time)) # we cut off the time at 3 decimals
                            duration, dotted = get_note_duration(start_time, end_time)
                            note_name = get_note(note)
                            octave = get_octave(note)
                            staff = get_staff(note_name, octave)

                            if (previous_note[0] != None and previous_note[0] - start_time > -0.06
                                and previous_note[1] == duration and previous_note[2] == dotted
                                and duration != "unknown"):
                                beat = beat - note_to_value(duration, dotted) # remove added beat from first note in chord
                                if beat < 0:
                                    beat = 0
                                chord = True
                            else:
                                chord = False

                            if beat != start_beat and backup != True:
                                print(f"{beat} != {start_beat}, Writing backup: {beat - start_beat}")
                                write_backup(beat - start_beat)
                                beat = start_beat
                                backup = True
                                voice = 2
                            
                            previous_note = (start_time, duration, dotted) # record for next note

                            print (f"Note: {note_name}, Octave: {octave}, Duration: {duration}, Dotted: {dotted}, Exact Duration: {d} seconds, Chord: {chord}")
                            last_note_end_time = time.time() # update the last_note_end_time to be when the key is released

                            if duration != "unknown":
                                if last_dynamic != dynamic and backup == False:
                                    generate_dynamic(dynamic, staff)
                                    last_dynamic = dynamic

                                beat, measure = generate_note(beat, measure, duration, note_name, octave, chord, voice, dotted, staff)
                                print(f"beat: {beat} measure: {measure}")

    finally:
        # Close the midi interface
        midi.quit()

        # write template_ending 
        with open("sheet.musicxml", "a") as file:
            file.writelines(template_ending)

# first line of code
# call main
main()