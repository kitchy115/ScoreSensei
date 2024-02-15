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

note_duration = {"quarter": 1,
                 "half": 2,
                 "whole": 4,
                 "eighth": 0.5,
                 "sixteenth": 0.25,
                 "thirty-second": 0.125}

duration_note = {1: "quarter",
                 2: "half",
                 4: "whole",
                 0.5: "eighth",
                 0.25: "sixteenth",
                 0.125: "thirty-second"}

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
        return "sixteenth"
    elif abs(THIRTY_SECOND_DURATION * error <= duration <= THIRTY_SECOND_DURATION / error):
        return "thirty-second"
    else:
        return "unknown"
    
def generate(beats, measure, duration, note_name, octave):
    # Generate and append MusicXML note entry
    with open("sheet.musicxml", "a") as file:
        if beats + note_duration[duration] > 4:
            file.writelines(note_template)
            file.write(f"<step>{note_name}</step>\n")
            if "#" in note_name:
                file.write("<alter>1</alter>\n")
            file.write(f"<octave>{octave}</octave>\n")
            file.write("</pitch>\n")
            first_note_duration = 4-beats # may need to be represented as a dotted note
            second_note_value = note_duration[duration]-(4-beats) # may need to be represented as a dotted note
            
        elif beats + note_duration[duration] == 4:
            return
        else:
            return

    return beats, measure

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

                        # determine beats in measure

                        # if beat of note is > beat remaning in measure
                        # use tied note, in first measure leave beat measure needs to be comeplete
                        # put remainder of note in other measure
                        # i.e. measure one has 3 beats, user plays a half note
                        # leave quater note in measure 1, create measure two
                        # tie last note in measure 1 to left over beat (one quarternote) in measure 2
                        beats, measure = generate(beats, measure, duration, note_name, octave)
                        
                        '''
                        if duration != "unknown":
                            file.writelines(note_template)
                            file.write(f"<step>{note_name}</step>\n")
                            if "#" in note_name:
                                file.write("<alter>1</alter>\n")
                            file.write(f"<octave>{octave}</octave>\n")
                            file.writelines(note_ending[duration])
                        '''   
finally:
    # Close the midi interface
    midi.quit()

    # write template_ending 
    with open("sheet.musicxml", "a") as file:
        file.writelines(template_ending)