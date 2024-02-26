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
    elif 30 <= velocity <= 39:
        return "pp"
    elif 40 <= velocity <= 49:
        return "p"
    elif 50 <= velocity <= 59:
        return "mp"
    elif 60 <= velocity <= 69:
        return "mf"
    elif 70 <= velocity <= 79:
        return "f"
    elif 80 <= velocity <= 89:
        return "ff"
    elif 90 <= velocity:
        return "fff"
    
def generate_note(beat, measure, duration, note_name, octave):
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
                    file.writelines(note_template)
                    file.write(f"<step>{note_name}</step>\n")
                    if "#" in note_name:
                        file.write("<alter>1</alter>\n")
                    file.write(f"<octave>{octave}</octave>\n")
                    file.write("</pitch>\n")
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
            file.writelines(note_template)
            file.write(f"<step>{note_name}</step>\n")
            if "#" in note_name:
                file.write("<alter>1</alter>\n")
            file.write(f"<octave>{octave}</octave>\n")
            file.write("</pitch>\n")
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
                    file.writelines(note_template)
                    file.write(f"<step>{note_name}</step>\n")
                    if "#" in note_name:
                        file.write("<alter>1</alter>\n")
                    file.write(f"<octave>{octave}</octave>\n")
                    file.write("</pitch>\n")
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
        if beat + note_to_value[duration] > 32:
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
        elif beat + note_to_value[duration] == 32:
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

    # maybe add if beats % 8 != 0
    # then add rests until beat is completed
    # i.e. measure has quarter note & eighth note
    # user rests for beat and 1/2
    # do eighth rest first, then quarter rest

    return beat, measure

def generate_dynamic(dynamic):
    # Generate and append MusicXML note entry
    with open("sheet.musicxml", "a") as file:
        file.write("<direction placement=\"below\">\n")
        file.write("<direction-type>\n")
        file.write("<dynamics>\n")
        file.write(f"<{dynamic}/>\n")
        file.write("</dynamics>\n")
        file.write("</direction-type>\n")
        file.write("</direction>\n")

note_start_times = {}
beat = 0
measure = 1
dyanmic = None
last_dynamic = None

try:
    print('*** Ready to play ***')
    print('**Press [q] to quit**')

    with open("sheet.musicxml", "w") as file:
        file.writelines(template)

    last_note_end_time = 0 # when the last note ends

    while not keyboard.is_pressed('q'):
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
                    note_start_times[note] = time.time()
                    #rest is calculated by the current notes start time - the last notes end time
                    if last_note_end_time != 0: #if this is not there, then it prints 0 when there is no rest
                        d = "{:.4f}".format(note_start_times[note] - last_note_end_time)
                        duration = get_note_duration(last_note_end_time, note_start_times[note])
                        print(f"Rest Time: {duration}, Exact Duration:{d} seconds")

                        if duration != "unknown":
                            beat, measure = generate_rest(beat, measure, duration)
                    
                    dynamic = get_dynamic(velocity)
                    print(f"{dyanmic} {velocity}")

                elif (status == 128) or (status == 144 and velocity == 0): # key released
                    if note in note_start_times:
                        start_time = note_start_times.pop(note, None)
                        end_time = time.time()
                        d = "{:.4f}".format(abs(start_time-end_time)) # we cut off the time at 3 decimals
                        duration = get_note_duration(start_time, end_time)
                        note_name = get_note(note)
                        octave = get_octave(note)

                        print (f"Note:{note_name}, Octave:{octave}, Duration:{duration}, Exact Duration:{d} seconds")
                        last_note_end_time = time.time() # update the last_note_end_time to be when the key is realized

                        if duration != "unknown":
                            if last_dynamic != dynamic:
                                generate_dynamic(dynamic)
                                last_dynamic = dynamic
                            
                            beat, measure = generate_note(beat, measure, duration, note_name, octave)
                            print(f"beat: {beat} measure: {measure}")
                        
finally:
    # Close the midi interface
    midi.quit()

    # write template_ending 
    with open("sheet.musicxml", "a") as file:
        file.writelines(template_ending)