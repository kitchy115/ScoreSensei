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

def get_note_duration(start_time, end_time, error):
    duration = end_time - start_time
 
    # error = .51

    beat_type = 1/4 # 1 beat = 1 quarter note (1/4 note)

                                                                    # in ?/4
    if abs(WHOLE_DURATION - WHOLE_DURATION * beat_type < duration): # 3s <
        return "whole"
    elif abs(HALF_DURATION - HALF_DURATION * beat_type < duration): # 1.5s <
        return "half"
    elif abs(QUARTER_DURATION - QUARTER_DURATION * beat_type < duration): # 0.75s < 
        return "quarter"
    elif abs(EIGHTH_DURATION - EIGHTH_DURATION * beat_type < duration): # 0.375s <
        return "eighth"
    elif abs(SIXTEENTH_DURATION - SIXTEENTH_DURATION * beat_type < duration): # 0.1875s <
        return "16th"
    elif abs(THIRTY_SECOND_DURATION < duration): # already so small
        return "32nd"
    else:
        return "unknown"

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
    
def generate_note(beat, measure, duration, note_name, octave, chord, voice):
    # Generate and append MusicXML note entry
    with open("sheet.musicxml", "a") as file:
        # determine beats in measure
        # if beat of note is > beat remaning in measure
        # use tied note, in first measure leave beat measure needs to be comeplete
        # put remainder of note in other measure
        # i.e. measure one has 3 beats, user plays a half note
        # leave quater note in measure 1, create measure two
        # tie last note in measure 1 to left over beat (one quarter note) in measure 2
        if beat + note_to_value[duration] > 32 and measureless == False:
            # add what can fit from this note into the measure
            file.write("<note>\n")
            if chord == True:
                file.write("<chord/>\n")
            file.write("<pitch>\n")
            file.write(f"<step>{note_name}</step>\n")
            if "#" in note_name:
                file.write("<alter>1</alter>\n")
            file.write(f"<octave>{octave}</octave>\n")
            file.write("</pitch>\n")
            # check that 32-beat can be displayed as a single note
            if 32-beat not in value_to_note: # cannot dislay as a single normal note
                # beginning of new stuff
                if check_dotted(32-beat) != 0: # display as single dotted note
                    file.write(f"<duration>{32-beat}</duration>\n")
                    file.write(f"<voice>{voice}</voice>\n")
                    file.write(f"<type>{value_to_note[calc_dotted(32-beat)]}</type>\n")
                    file.write("<dot/>\n")
                    file.write("<notations>\n")
                    file.write("<tied type=\"start\"/>\n")
                    file.write("</notations>\n")
                    file.write("</note>\n")
                else: # display two tied notes 
                    # display first of two
                    file.write(f"<duration>{32-beat-get_closest_note(32-beat)}</duration>\n")
                    file.write(f"<voice>{voice}</voice>\n")
                    if 32-beat-get_closest_note(32-beat) not in value_to_note:
                        # represent as dotted
                        file.write(f"<type>{value_to_note[calc_dotted(32-beat-get_closest_note(32-beat))]}</type>\n")
                        file.write("<dot/>\n")
                    else:
                        # represent as normal note
                        file.write(f"<type>{value_to_note[32-beat-get_closest_note(32-beat)]}</type>\n")
                    file.write("<notations>\n")
                    file.write("<tied type=\"start\"/>\n")
                    file.write("</notations>\n")
                    file.write("</note>\n")
                    # display the second note
                    file.write("<note>\n")
                    if chord == True:
                        file.write("<chord/>\n")
                    file.write("<pitch>\n")
                    file.write(f"<step>{note_name}</step>\n")
                    if "#" in note_name:
                        file.write("<alter>1</alter>\n")
                    file.write(f"<octave>{octave}</octave>\n")
                    file.write("</pitch>\n")
                    file.write(f"<duration>{get_closest_note(32-beat)}</duration>\n")
                    file.write(f"<voice>{voice}</voice>\n")
                    if get_closest_note(32-beat) not in value_to_note:
                        # represent as dotted
                        file.write(f"<type>{value_to_note[calc_dotted(get_closest_note(32-beat))]}</type>\n")
                        file.write("<dot/>\n")
                    else:
                        # represent as normal note
                        file.write(f"<type>{value_to_note[get_closest_note(32-beat)]}</type>\n")
                    file.write("<notations>\n")
                    file.write("<tied type=\"stop\"/>\n")
                    file.write("<tied type=\"start\"/>\n")
                    file.write("</notations>\n")
                    file.write("</note>\n")
                    # end of new stuff
            else:
                # display as a single normal note
                file.write(f"<duration>{32-beat}</duration>\n")
                file.write(f"<voice>{voice}</voice>\n")
                file.write(f"<type>{value_to_note[32-beat]}</type>\n")
                file.write("<notations>\n")
                file.write("<tied type=\"start\"/>\n")
                file.write("</notations>\n")
                file.write("</note>\n")
            file.write("</measure>\n")
            measure += 1
            # create new measure
            file.write(f"<measure number=\"{measure}\">\n")
            file.write("<note>\n")
            if chord == True:
                file.write("<chord/>\n")
            file.write("<pitch>\n")
            file.write(f"<step>{note_name}</step>\n")
            if "#" in note_name:
                file.write("<alter>1</alter>\n")
            file.write(f"<octave>{octave}</octave>\n")
            file.write("</pitch>\n")
            # check if note can be displayed as one or need to be split into two notes
            if note_to_value[duration] - (32-beat) not in value_to_note:
                if check_dotted(note_to_value[duration] - (32-beat)) != 0: # display as single dotted note
                    file.write(f"<duration>{note_to_value[duration] - (32-beat)}</duration>\n")
                    file.write(f"<voice>{voice}</voice>\n")
                    file.write(f"<type>{value_to_note[calc_dotted(note_to_value[duration] - (32-beat))]}</type>\n")
                    file.write("<dot/>\n")
                    file.write("<notations>\n")
                    file.write("<tied type=\"stop\"/>\n")
                    file.write("</notations>\n")
                    file.write("</note>\n")
                else: # display two tied notes
                    # display first of two
                    file.write(f"<duration>{note_to_value[duration] - (32-beat)-get_closest_note(note_to_value[duration] - (32-beat))}</duration>\n")
                    file.write(f"<voice>{voice}</voice>\n")
                    if note_to_value[duration] - (32-beat)-get_closest_note(note_to_value[duration] - (32-beat)) not in value_to_note:
                        # represent as dotted
                        file.write(f"<type>{value_to_note[calc_dotted(note_to_value[duration] - (32-beat)-get_closest_note(note_to_value[duration] - (32-beat)))]}</type>\n")
                        file.write("<dot/>\n")
                    else:
                        # represent as normal note
                        file.write(f"<type>{value_to_note[note_to_value[duration] - (32-beat)-get_closest_note(note_to_value[duration] - (32-beat))]}</type>\n")
                    file.write("<notations>\n")
                    file.write("<tied type=\"stop\"/>\n")
                    file.write("<tied type=\"start\"/>\n")
                    file.write("</notations>\n")
                    file.write("</note>\n")
                    # display the second note
                    file.write("<note>\n")
                    if chord == True:
                        file.write("<chord/>\n")
                    file.write("<pitch>\n")
                    file.write(f"<step>{note_name}</step>\n")
                    if "#" in note_name:
                        file.write("<alter>1</alter>\n")
                    file.write(f"<octave>{octave}</octave>\n")
                    file.write("</pitch>\n")
                    file.write(f"<duration>{get_closest_note(note_to_value[duration] - (32-beat))}</duration>\n")
                    file.write(f"<voice>{voice}</voice>\n")
                    if get_closest_note(note_to_value[duration] - (32-beat)) not in value_to_note:
                        # represent as dotted
                        file.write(f"<type>{value_to_note[calc_dotted(get_closest_note(note_to_value[duration] - (32-beat)))]}</type>\n")
                        file.write("<dot/>\n")
                    else:
                        # represent as normal note
                        file.write(f"<type>{value_to_note[get_closest_note(note_to_value[duration] - (32-beat))]}</type>\n")
                    file.write("<notations>\n")
                    file.write("<tied type=\"stop\"/>\n")
                    file.write("</notations>\n")
                    file.write("</note>\n")
            else:
                # display as one normal note
                file.write(f"<duration>{note_to_value[duration] - (32-beat)}</duration>\n")
                file.write(f"<voice>{voice}</voice>\n")
                file.write(f"<type>{value_to_note[note_to_value[duration] - (32-beat)]}</type>\n")
                file.write("<notations>\n")
                file.write("<tied type=\"stop\"/>\n")
                file.write("</notations>\n")
                file.write("</note>\n")
            if chord == False:
                beat = note_to_value[duration] - (32-beat)
            # check if another tied note needs to be displayed
        elif beat + note_to_value[duration] == 32 and measureless == False:
            file.write("<note>\n")
            if chord == True:
                file.write("<chord/>\n")
            file.write("<pitch>\n")
            file.write(f"<step>{note_name}</step>\n")
            if "#" in note_name:
                file.write("<alter>1</alter>\n")
            file.write(f"<octave>{octave}</octave>\n")
            file.write("</pitch>\n")
            file.write(f"<duration>{note_to_value[duration]}</duration>\n")
            file.write(f"<voice>{voice}</voice>\n")
            file.write(f"<type>{duration}</type>\n")
            file.write("</note>\n")
            if chord == False:
                file.write("</measure>\n")
                measure += 1
                beat = 0
                file.write(f"<measure number=\"{measure}\">\n")
        else:
            file.write("<note>\n")
            if chord == True:
                file.write("<chord/>\n")
            file.write("<pitch>\n")
            file.write(f"<step>{note_name}</step>\n")
            if "#" in note_name:
                file.write("<alter>1</alter>\n")
            file.write(f"<octave>{octave}</octave>\n")
            file.write("</pitch>\n")
            file.write(f"<duration>{note_to_value[duration]}</duration>\n")
            file.write(f"<voice>{voice}</voice>\n")
            file.write(f"<type>{duration}</type>\n")
            file.write("</note>\n")
            if chord == False:
                beat += note_to_value[duration]

    return beat, measure

def generate_rest(beat, measure, duration):
    # Generate and append MusicXML note entry
    with open("sheet.musicxml", "a") as file:
        # determine beats in measure
        # if beat of note is > beat remaning in measure
        # use tied note, in first measure leave beat measure needs to be comeplete
        # put remainder of note in other measure
        # i.e. measure one has 3 beats, user plays a half note
        # leave quater note in measure 1, create measure two
        # tie last note in measure 1 to left over beat (one quarter note) in measure 2
        if beat + note_to_value[duration] > 32 and measureless == False:
            # add what can fit from this note into the measure
            file.write("<note>\n")
            file.write("<rest/>\n")
            # check that 32-beat can be displayed as a single note
            if 32-beat not in value_to_note: # cannot dislay as a single normal note
                # beginning of new stuff
                if check_dotted(32-beat) != 0: # display as single dotted note
                    file.write(f"<duration>{32-beat}</duration>\n")
                    file.write(f"<type>{value_to_note[calc_dotted(32-beat)]}</type>\n")
                    file.write("<dot/>\n")
                    file.write("<notations>\n")
                    file.write("<tied type=\"start\"/>\n")
                    file.write("</notations>\n")
                    file.write("</note>\n")
                else: # display two tied notes 
                    # display first of two
                    file.write(f"<duration>{32-beat-get_closest_note(32-beat)}</duration>\n")
                    if 32-beat-get_closest_note(32-beat) not in value_to_note:
                        # represent as dotted
                        file.write(f"<type>{value_to_note[calc_dotted(32-beat-get_closest_note(32-beat))]}</type>\n")
                        file.write("<dot/>\n")
                    else:
                        # represent as normal note
                        file.write(f"<type>{value_to_note[32-beat-get_closest_note(32-beat)]}</type>\n")
                    file.write("<notations>\n")
                    file.write("<tied type=\"start\"/>\n")
                    file.write("</notations>\n")
                    file.write("</note>\n")
                    # display the second note
                    file.write("<note>\n")
                    file.write("<rest/>\n")
                    file.write(f"<duration>{get_closest_note(32-beat)}</duration>\n")
                    if get_closest_note(32-beat) not in value_to_note:
                        # represent as dotted
                        file.write(f"<type>{value_to_note[calc_dotted(get_closest_note(32-beat))]}</type>\n")
                        file.write("<dot/>\n")
                    else:
                        # represent as normal note
                        file.write(f"<type>{value_to_note[get_closest_note(32-beat)]}</type>\n")
                    file.write("<notations>\n")
                    file.write("<tied type=\"stop\"/>\n")
                    file.write("<tied type=\"start\"/>\n")
                    file.write("</notations>\n")
                    file.write("</note>\n")
                    # end of new stuff
            else:
                # display as a single normal note
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
            file.write("<note>\n")
            file.write("<rest/>\n")
            # check if note can be displayed as one or need to be split into two notes
            if note_to_value[duration] - (32-beat) not in value_to_note:
                if check_dotted(note_to_value[duration] - (32-beat)) != 0: # display as single dotted note
                    file.write(f"<duration>{note_to_value[duration] - (32-beat)}</duration>\n")
                    file.write(f"<type>{value_to_note[calc_dotted(note_to_value[duration] - (32-beat))]}</type>\n")
                    file.write("<dot/>\n")
                    file.write("<notations>\n")
                    file.write("<tied type=\"stop\"/>\n")
                    file.write("</notations>\n")
                    file.write("</note>\n")
                else: # display two tied notes
                    # display first of two
                    file.write(f"<duration>{note_to_value[duration] - (32-beat)-get_closest_note(note_to_value[duration] - (32-beat))}</duration>\n")
                    if note_to_value[duration] - (32-beat)-get_closest_note(note_to_value[duration] - (32-beat)) not in value_to_note:
                        # represent as dotted
                        file.write(f"<type>{value_to_note[calc_dotted(note_to_value[duration] - (32-beat)-get_closest_note(note_to_value[duration] - (32-beat)))]}</type>\n")
                        file.write("<dot/>\n")
                    else:
                        # represent as normal note
                        file.write(f"<type>{value_to_note[note_to_value[duration] - (32-beat)-get_closest_note(note_to_value[duration] - (32-beat))]}</type>\n")
                    file.write("<notations>\n")
                    file.write("<tied type=\"stop\"/>\n")
                    file.write("<tied type=\"start\"/>\n")
                    file.write("</notations>\n")
                    file.write("</note>\n")
                    # display the second note
                    file.write("<note>\n")
                    file.write("<rest/>\n")
                    file.write(f"<duration>{get_closest_note(note_to_value[duration] - (32-beat))}</duration>\n")
                    if get_closest_note(note_to_value[duration] - (32-beat)) not in value_to_note:
                        # represent as dotted
                        file.write(f"<type>{value_to_note[calc_dotted(get_closest_note(note_to_value[duration] - (32-beat)))]}</type>\n")
                        file.write("<dot/>\n")
                    else:
                        # represent as normal note
                        file.write(f"<type>{value_to_note[get_closest_note(note_to_value[duration] - (32-beat))]}</type>\n")
                    file.write("<notations>\n")
                    file.write("<tied type=\"stop\"/>\n")
                    file.write("</notations>\n")
                    file.write("</note>\n")
            else:
                # display as one normal note
                file.write(f"<duration>{note_to_value[duration] - (32-beat)}</duration>\n")
                file.write(f"<type>{value_to_note[note_to_value[duration] - (32-beat)]}</type>\n")
                file.write("<notations>\n")
                file.write("<tied type=\"stop\"/>\n")
                file.write("</notations>\n")
                file.write("</note>\n")
            beat = note_to_value[duration] - (32-beat)
            # check if another tied note needs to be displayed
        elif beat + note_to_value[duration] == 32 and measureless == False:
            file.write("<note>\n")
            file.write("<rest/>\n")
            file.write(f"<duration>{note_to_value[duration]}</duration>\n")
            file.write(f"<type>{duration}</type>\n")
            file.write("</note>\n")
            file.write("</measure>\n")
            measure += 1
            beat = 0
            file.write(f"<measure number=\"{measure}\">\n")
        else:
            file.write("<note>\n")
            file.write("<rest/>\n")
            file.write(f"<duration>{note_to_value[duration]}</duration>\n")
            file.write(f"<type>{duration}</type>\n")
            file.write("</note>\n")
            beat += note_to_value[duration]

    return beat, measure

note_start_times = {}
beat = 0
measure = 1
previous_note = (None, None) # (start_time, duration)
chord = False
backup = False # flag for when a <backup> is used (needed to know when to place a <forward>)
last_note_start_time = 0
voice = 1
measureless = True

try:
    print('*** Ready to play ***')
    print('**Press [q] to quit**')

    with open("sheet.musicxml", "w") as file:
        file.writelines(template)

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
                    print(f"Start time: {note_start_times[note][0]}, Start beat: {note_start_times[note][1]}")
                    #rest is calculated by the current notes start time - the last notes end time

                    # prevent chords from cloning rests, might need to tweak -0.06
                    if last_note_end_time != 0 and last_note_start_time - note_start_times[note][0] < -0.06: #if this is not there, then it prints 0 when there is no rest
                        if backup == True:
                            backup = False
                            voice = 1
                        if chord == True:
                            beat = beat + note_to_value[previous_note[1]]
                            note_start_times[note] = (note_start_times[note][0], beat)
                            print(f"Updated start beat: {start_beat}")
                            if beat == 32 and measureless == False:
                                with open("sheet.musicxml", "a") as file:
                                    file.write("</measure>\n")
                                    measure += 1
                                    beat = 0
                                    file.write(f"<measure number=\"{measure}\">\n")
                            chord = False

                        
                        d = "{:.4f}".format(note_start_times[note][0] - last_note_end_time)
                        duration = get_note_duration(last_note_end_time, note_start_times[note][0], 0.83)
                        print(f"Rest Time: {duration}, Exact Duration:{d} seconds")

                        if duration != "unknown":
                            beat, measure = generate_rest(beat, measure, duration)
                            note_start_times[note] = (note_start_times[note][0], beat) # update starting beat for note
                            print(f"Updated start beat: {note_start_times[note][1]}")
                        last_note_start_time = note_start_times[note][0] # record start time for next note  

                elif (status == 128) or (status == 144 and velocity == 0):  # key released
                    if note in note_start_times:
                        start_time, start_beat = note_start_times.pop(note, None)
                        end_time = time.time()
                        d = "{:.4f}".format(abs(start_time-end_time)) # we cut off the time at 3 decimals
                        duration = get_note_duration(start_time, end_time, 0.51)
                        note_name = get_note(note)
                        octave = get_octave(note)

                        if (previous_note[0] != None and previous_note[0] - start_time > -0.06
                            and previous_note[1] == duration):
                            if chord == False:
                                if measure == 0 and measureless == False: # must remove newly created measure
                                    with open("sheet.musicxml", "r+") as file:
                                        lines = file.readlines()
                                        file.seek(0)
                                        file.truncate()
                                        file.writelines(lines[:-2])
                                beat = beat - note_to_value[duration] # remove added beat from first note in chord
                                if beat < 0:
                                    beat = 0
                            chord = True
                        #else:
                            #if chord == True:
                                #beat = beat + note_to_value[previous_note[1]]
                                #start_beat = beat
                                #print(f"Updated start beat: {start_beat}")
                                #if beat == 32 and measureless == False:
                                    #with open("sheet.musicxml", "a") as file:
                                        #file.write("</measure>\n")
                                        #measure += 1
                                        #beat = 0
                                        #file.write(f"<measure number=\"{measure}\">\n")
                            #chord = False

                        if beat != start_beat and backup != True:
                            print(f"{beat} != {start_beat}, Writing backup:{beat - start_beat}")
                            write_backup(beat - start_beat)
                            beat = start_beat
                            backup = True
                            voice = 2
                        
                        previous_note = (start_time, duration) # record for next note

                        print (f"Note:{note_name}, Octave:{octave}, Duration:{duration}, Exact Duration:{d} seconds, Chord:{chord}")
                        last_note_end_time = time.time() # update the last_note_end_time to be when the key is released

                        if duration != "unknown":
                            beat, measure = generate_note(beat, measure, duration, note_name, octave, chord, voice)
                            print(f"beat: {beat} measure: {measure}")
                        
finally:
    # Close the midi interface
    midi.quit()

    # write template_ending 
    with open("sheet.musicxml", "a") as file:
        file.writelines(template_ending)