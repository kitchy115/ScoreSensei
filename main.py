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
          "32nd": 1,
          "unknown": 0}

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

    # TODO fix conflicts when duration > whole
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
    # remove below
    # elif abs((THIRTY_SECOND_DURATION + THIRTY_SECOND_DURATION / 2) - ((THIRTY_SECOND_DURATION + THIRTY_SECOND_DURATION / 2) - THIRTY_SECOND_DURATION) / 2 < duration):
        # return "32nd", True
    # remove above
    elif abs(THIRTY_SECOND_DURATION < duration):
        return "32nd", False
    else:
        return "unknown", False

# only used for tying notes between measures
def get_closest_note(leftover):
    if leftover >= 32:
        return "whole", False
    elif leftover >= (16 + 8):
        return "half", True
    elif leftover >= 16:
        return "half", False
    elif leftover >= (8 + 4):
        return "quarter", True
    elif leftover >= 8:
        return "quarter", False
    elif leftover >= (4 + 2):
        return "eighth", True
    elif leftover >= 4:
        return "eighth", False
    elif leftover >= (2 + 1):
        return "16th", True
    elif leftover >= 2:
        return "16th", False
    elif leftover >= (1 + 0.5):
        return "32nd", True
    elif leftover >= 1:
        return "32nd", False
    else:
        return "unknown", False
    
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
    
def generate_note(beat, create_measure, duration, note_name, octave, chord, voice, dotted, staff, time_sig_beats, l1_note_buffer, l2_note_buffer, tied):
    # Generate and append MusicXML note entry
    with open("sheet.musicxml", "a") as file:
        next_tied = tied
        if note_to_value(duration, dotted) + beat >= time_sig_beats * 8: # and chord == False:
            # create new measure
            create_measure = True
            next_tied = True
            # write leftover tied notes to note_buffer
            leftover = note_to_value(duration, dotted) - (time_sig_beats * 8 - beat)
            duration, dotted = get_closest_note(time_sig_beats * 8 - beat)
            if leftover != 0:
                # calc first note
                l1_duration, l1_dotted = get_closest_note(leftover)
                leftover = leftover - note_to_value(l1_duration, l1_dotted)
                l2 = False
                if leftover != 0:
                    # calc second note
                    l2 = True
                    l2_duration, l2_dotted = get_closest_note(leftover)

                if l1_duration != "unknown":
                    # write l1 to buffer
                    l1_note_buffer.append("<note>\n")
                    if chord == True:
                        l1_note_buffer.append("<chord/>\n")
                    l1_note_buffer.append("<pitch>\n")
                    l1_note_buffer.append(f"<step>{note_name}</step>\n")
                    if "#" in note_name:
                        l1_note_buffer.append("<alter>1</alter>\n")
                    l1_note_buffer.append(f"<octave>{octave}</octave>\n")
                    l1_note_buffer.append("</pitch>\n")
                    l1_note_buffer.append(f"<duration>{note_to_value(l1_duration, l1_dotted)}</duration>\n")
                    l1_note_buffer.append(f"<voice>{voice}</voice>\n")
                    l1_note_buffer.append(f"<type>{l1_duration}</type>\n")
                    if l1_dotted == True:
                        l1_note_buffer.append(f"<dot/>\n")
                    l1_note_buffer.append(f"<staff>{staff}</staff>\n")
                    l1_note_buffer.append("<notations>\n")
                    l1_note_buffer.append("<tied type=\"stop\"/>\n")
                    l1_note_buffer.append("<tied type=\"start\"/>\n")
                    l1_note_buffer.append("</notations>\n")
                    l1_note_buffer.append("</note>\n")

                if l2 == True and l2_duration != "unknown":
                    # write l2 to buffer
                    l2_note_buffer.append("<note>\n")
                    if chord == True:
                        l2_note_buffer.append("<chord/>\n")
                    l2_note_buffer.append("<pitch>\n")
                    l2_note_buffer.append(f"<step>{note_name}</step>\n")
                    if "#" in note_name:
                        l2_note_buffer.append("<alter>1</alter>\n")
                    l2_note_buffer.append(f"<octave>{octave}</octave>\n")
                    l2_note_buffer.append("</pitch>\n")
                    l2_note_buffer.append(f"<duration>{note_to_value(l2_duration, l2_dotted)}</duration>\n")
                    l2_note_buffer.append(f"<voice>{voice}</voice>\n")
                    l2_note_buffer.append(f"<type>{l2_duration}</type>\n")
                    if l2_dotted == True:
                        l2_note_buffer.append(f"<dot/>\n")
                    l2_note_buffer.append(f"<staff>{staff}</staff>\n")
                    l2_note_buffer.append("<notations>\n")
                    l2_note_buffer.append("<tied type=\"stop\"/>\n")
                    l2_note_buffer.append("<tied type=\"start\"/>\n")
                    l2_note_buffer.append("</notations>\n")
                    l2_note_buffer.append("</note>\n")

        # write the note
        if duration != "unknown":
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
            if create_measure == True and tied == False:
                file.write("<notations>\n")
                file.write("<tied type=\"start\"/>\n")
                file.write("</notations>\n")
            elif create_measure == False and tied == True:
                file.write("<notations>\n")
                file.write("<tied type=\"stop\"/>\n")
                file.write("</notations>\n")
            elif create_measure == True and tied == True:
                file.write("<notations>\n")
                file.write("<tied type=\"stop\"/>\n")
                file.write("<tied type=\"start\"/>\n")
                file.write("</notations>\n")
            file.write("</note>\n")
            if create_measure == False and chord == False:
                beat += note_to_value(duration, dotted)

    return beat, create_measure, l1_note_buffer, l2_note_buffer, next_tied

def generate_rest(beat, create_measure, duration, dotted, time_sig_beats, l1_note_buffer, l2_note_buffer):
    # Generate and append MusicXML note entry
    with open("sheet.musicxml", "a") as file:
        # TODO add staff support and <forward>
        if note_to_value(duration, dotted) + beat >= time_sig_beats * 8: # create new measure
            create_measure = True
            # write leftover tied notes to note_buffer
            leftover = note_to_value(duration, dotted) - (time_sig_beats * 8 - beat)
            duration, dotted = get_closest_note(time_sig_beats * 8 - beat)
            if leftover != 0:
                # calc first note
                l1_duration, l1_dotted = get_closest_note(leftover)
                leftover = leftover - note_to_value(l1_duration, l1_dotted)
                l2 = False
                if leftover != 0:
                    # calc second note
                    l2 = True
                    l2_duration, l2_dotted = get_closest_note(leftover)
                
                if l1_duration != "unknown":
                    # write l1 to buffer
                    l1_note_buffer.append("<note>\n")
                    l1_note_buffer.append("<rest/>\n")
                    l1_note_buffer.append(f"<duration>{note_to_value(l1_duration, l1_dotted)}</duration>\n")
                    l1_note_buffer.append(f"<type>{l1_duration}</type>\n")
                    if dotted == True:
                        l1_note_buffer.append(f"<dot/>\n")
                    l1_note_buffer.append("</note>\n")

                if l2 == True and l2_duration != "unknown":
                    # write l2 to buffer
                    l2_note_buffer.append("<note>\n")
                    l2_note_buffer.append("<rest/>\n")
                    l2_note_buffer.append(f"<duration>{note_to_value(l2_duration, l2_dotted)}</duration>\n")
                    l2_note_buffer.append(f"<type>{l2_duration}</type>\n")
                    if dotted == True:
                        l2_note_buffer.append(f"<dot/>\n")
                    l2_note_buffer.append("</note>\n")
        
        if duration != "unknown":
            file.write("<note>\n")
            file.write("<rest/>\n")
            file.write(f"<duration>{note_to_value(duration, dotted)}</duration>\n")
            file.write(f"<type>{duration}</type>\n")
            if dotted == True:
                file.write(f"<dot/>\n")
            file.write("</note>\n")
            if create_measure == False:
                beat += note_to_value(duration, dotted)

    return beat, create_measure, l1_note_buffer, l2_note_buffer

# main(midi_note, file_name)
def main():
    note_start_times = {}
    buffer_note_start_times = {}
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
    create_measure = False
    l1_note_buffer = []
    l2_note_buffer = []

    try:
        print('*** Ready to play ***')
        print('**Press [`] to quit**')

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
                        note_start_times[note] = (time.time(), beat, False) # record start time and amount of beats in measure (used by <backup>)
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
                                beat, create_measure, l1_note_buffer, l2_note_buffer = generate_rest(beat, create_measure, duration, dotted, time_sig_beats, l1_note_buffer, l2_note_buffer)
                                
                                note_start_times[note] = (note_start_times[note][0], beat, False) # update starting beat for note
                                print(f"Updated start beat: {note_start_times[note][1]}")
                        
                        last_note_start_time = note_start_times[note][0] # record start time for next note

                    elif (status == 128) or (status == 144 and velocity == 0): # key released
                        if note in note_start_times:
                            start_time, start_beat, tied = note_start_times.pop(note, None)
                            end_time = time.time()
                            d = "{:.4f}".format(abs(start_time-end_time)) # we cut off the time at 3 decimals
                            duration, dotted = get_note_duration(start_time, end_time)
                            note_name = get_note(note)
                            octave = get_octave(note)
                            staff = get_staff(note_name, octave)

                            if (previous_note[0] != None and previous_note[0] - start_time > -0.06
                                and previous_note[1] == duration and previous_note[2] == dotted
                                and duration != "unknown"):
                                chord = True
                            else:
                                chord = False

                            if beat != start_beat and backup != True and duration != "unknown" and chord == False:
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

                                beat, create_measure, l1_note_buffer, l2_note_buffer, tied = generate_note(beat, create_measure, duration, note_name, octave, chord, voice, dotted, staff, time_sig_beats, l1_note_buffer, l2_note_buffer, tied)
                                print(f"beat: {beat} measure: {measure}")
                            
                    if create_measure == True:
                        new_beat = note_to_value(duration, dotted) - (time_sig_beats * 8 - beat) # record leftover from first note
                        for note in note_start_times:
                            # TODO generate unique voices for each non-chord note
                            # TODO thoroughly test
                            start_time, start_beat, tied = note_start_times[note]
                            end_time = time.time()
                            d = "{:.4f}".format(abs(start_time-end_time)) # we cut off the time at 3 decimals
                            duration, dotted = get_note_duration(start_time, end_time)
                            note_name = get_note(note)
                            octave = get_octave(note)
                            staff = get_staff(note_name, octave)

                            if (previous_note[0] != None and previous_note[0] - start_time > -0.06
                                and previous_note[1] == duration and previous_note[2] == dotted
                                and duration != "unknown"):
                                chord = True
                            else:
                                chord = False

                            if beat != start_beat and backup != True and duration != "unknown" and chord == False:
                                # end of measure, can assume beat is max
                                print(f"{time_sig_beats * 8} != {start_beat}, Writing backup: {time_sig_beats * 8 - start_beat}")
                                write_backup(time_sig_beats * 8 - start_beat)
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

                                beat, create_measure, l1_note_buffer, l2_note_buffer, tied = generate_note(beat, create_measure, duration, note_name, octave, chord, voice, dotted, staff, time_sig_beats, l1_note_buffer, l2_note_buffer, tied)
                                print(f"beat: {beat} measure: {measure}")

                            # push copy of note back onto note_start_times
                            leftover = note_to_value(duration, dotted) - (time_sig_beats * 8 - beat)
                            if leftover < 0: # when note duration is 0
                                leftover = 0
                            if leftover > new_beat:
                                new_beat = leftover
                            if duration != "unknown":
                                buffer_note_start_times[note] = (time.time(), leftover, tied)
                            else:
                                buffer_note_start_times[note] = (time.time(), new_beat, tied)
                        # end of for each loop

                        if backup == True:
                            backup = False
                            voice = 1
                        if chord == True:
                            chord = False
                        
                        # write the new measure
                        measure += 1
                        with open("sheet.musicxml", "a") as file:
                            file.write("</measure>\n")
                            file.write(f"<measure number=\"{measure}\">\n")
                            file.writelines(l1_note_buffer)
                            file.writelines(l2_note_buffer)
                        create_measure = False
                        beat = new_beat
                        l1_note_buffer = [] # clear buffer
                        l2_note_buffer = [] # clear buffer
                        note_start_times = buffer_note_start_times
                        buffer_note_start_times = {} # clear buffer dict

    finally:
        # Close the midi interface
        midi.quit()

        # write template_ending 
        with open("sheet.musicxml", "a") as file:
            file.writelines(template_ending)

# first line of code
main() # call main