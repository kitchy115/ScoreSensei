n_to_v = {"quarter": 8,
          "half": 16,
          "whole": 32,
          "eighth": 4,
          "16th": 2,
          "32nd": 1,
          "unknown": 0}

# seems useless as a function now
def get_note(note_number, note_names):
    return note_names[note_number % 12]

def get_octave(note_number):
    return (note_number // 12) - 1 # // = truncating division

def get_note_duration(start_time, end_time, bpm):
    duration = end_time - start_time

    quarter_duration = 60 / bpm
    half_duration = 2 * quarter_duration
    whole_duration = 4 * quarter_duration
    eighth_duration = quarter_duration / 2
    sixteenth_duration = quarter_duration / 4
    thirty_second_duration = quarter_duration / 8

    # TODO fix conflicts when duration > whole
    if abs(whole_duration - (whole_duration - (half_duration + quarter_duration)) / 2 < duration):
        return "whole", False
    elif abs((half_duration + quarter_duration) - ((half_duration + quarter_duration) - half_duration) / 2 < duration):
        return "half", True
    elif abs(half_duration - (half_duration - (quarter_duration + eighth_duration)) / 2 < duration):
        return "half", False
    elif abs((quarter_duration + eighth_duration) - ((quarter_duration + eighth_duration) - quarter_duration) / 2 < duration):
        return "quarter", True
    elif abs(quarter_duration - (quarter_duration - (eighth_duration + sixteenth_duration)) / 2 < duration):
        return "quarter", False
    elif abs((eighth_duration + sixteenth_duration) - ((eighth_duration + sixteenth_duration) - eighth_duration) / 2 < duration):
        return "eighth", True
    elif abs(eighth_duration - (eighth_duration - (sixteenth_duration + thirty_second_duration)) / 2 < duration):
        return "eighth", False
    elif abs((sixteenth_duration + thirty_second_duration) - ((sixteenth_duration + thirty_second_duration) - sixteenth_duration) / 2 < duration):
        return "16th", True
    elif abs(sixteenth_duration - (sixteenth_duration - (thirty_second_duration + thirty_second_duration / 2)) / 2 < duration):
        return "16th", False
    elif abs(thirty_second_duration < duration):
        return "32nd", False
    else:
        return "unknown", False

# only used for tying notes between measures
def get_remainder_notes(leftover):
    if leftover >= 32:
        return "whole", False, ("unknown", False)
    elif leftover > (16 + 8):
        return "half", True, get_closest_note(leftover - (16 + 8))
    elif leftover == (16 + 8):
        return "half", True, ("unknown", False)
    elif leftover > 16:
        return "half", False, get_closest_note(leftover - 16)
    elif leftover == 16:
        return "half", False, ("unknown", False)
    elif leftover > (8 + 4):
        return "quarter", True, get_closest_note(leftover - (8 + 4))
    elif leftover == (8 + 4):
        return "quarter", True, ("unknown", False)
    elif leftover > 8:
        return "quarter", False, get_closest_note(leftover - 8)
    elif leftover == 8:
        return "quarter", False, ("unknown", False)
    elif leftover > (4 + 2):
        return "eighth", True, get_closest_note(leftover - (4 + 2))
    elif leftover == (4 + 2):
        return "eighth", True, ("unknown", False)
    elif leftover > 4:
        return "eighth", False, get_closest_note(leftover - 4)
    elif leftover == 4:
        return "eighth", False, ("unknown", False)
    elif leftover > (2 + 1):
        return "16th", True, get_closest_note(leftover - (2 + 1))
    elif leftover == (2 + 1):
        return "16th", True, ("unknown", False)
    elif leftover > 2:
        return "16th", False, get_closest_note(leftover - 2)
    elif leftover == 2:
        return "16th", False, ("unknown", False)
    elif leftover >= 1:
        return "32nd", False, ("unknown", False)
    else:
        return "unknown", False, ("unknown", False)

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
    elif leftover >= 1:
        return "32nd", False
    else:
        return "unknown", False
    
def get_dynamic(velocity):
    if velocity >= 126:
        return "fff"
    elif velocity >= 112:
        return "ff"
    elif velocity >= 96:
        return "f"
    elif velocity >= 80:
        return "mf"
    elif velocity >= 64:
        return "mp"
    elif velocity >= 48:
        return "p"
    elif velocity >= 32:
        return "pp"
    elif velocity >= 16:
        return "ppp"
    else:
        return "unknown"
    
def note_to_value(duration, dotted):
    result = n_to_v[duration]
    if dotted == True:
        result = result + n_to_v[duration] / 2
    return result

def get_staff(octave):
    if octave < 4: # less than C4
        return 2
    else:
        return 1 # C4 or greater

def write_backup(beat, xml_fp):
    xml_fp.write("<backup>\n")
    xml_fp.write(f"<duration>{beat}</duration>\n")
    xml_fp.write("</backup>\n")

def write_forward(beat, xml_fp):
    xml_fp.write("<foward>\n")
    xml_fp.write(f"<duration>{beat}</duration>\n")
    xml_fp.write("</foward>\n")

def generate_dynamic(dynamic, staff, xml_fp):
    # Generate and append MusicXML note entry
    if staff == 1:
        xml_fp.write("<direction placement=\"below\">\n")
    else:
        xml_fp.write("<direction placement=\"above\">\n")
    xml_fp.write("<direction-type>\n")
    xml_fp.write("<dynamics>\n")
    xml_fp.write(f"<{dynamic}/>\n")
    xml_fp.write("</dynamics>\n")
    xml_fp.write("</direction-type>\n")
    xml_fp.write(f"<staff>{staff}</staff>\n")
    xml_fp.write("</direction>\n")
    
def generate_note(beat, create_measure, duration, note_name, octave, chord, voice, dotted, staff, time_sig_beats, l1_note_buffer, l2_note_buffer, tied, xml_fp):
    # Generate and append MusicXML note entry
    next_tied = tied
    if (create_measure == True) or (note_to_value(duration, dotted) + beat >= time_sig_beats * 8 and chord == False):
        # create new measure
        create_measure = True
        next_tied = True
        # write leftover tied notes to note_buffer
        leftover = note_to_value(duration, dotted) - (time_sig_beats * 8 - beat)
        # check if old measure remainder can be expressed in one note or two notes
        # duration, dotted, next_note = get_remainder_notes(time_sig_beats * 8 - beat) # next_note = (next_duration, next_dotted)
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
                l1_note_buffer.append(f"<step>{note_name[0]}</step>\n")
                if "#" in note_name:
                    l1_note_buffer.append("<alter>1</alter>\n")
                elif "b" in note_name:
                    l1_note_buffer.append("<alter>-1</alter>\n")
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
                l2_note_buffer.append(f"<step>{note_name[0]}</step>\n")
                if "#" in note_name:
                    l2_note_buffer.append("<alter>1</alter>\n")
                elif "b" in note_name:
                    l2_note_buffer.append("<alter>-1</alter>\n")
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
        xml_fp.write("<note>\n")
        if chord == True:
            xml_fp.write("<chord/>\n")
        xml_fp.write("<pitch>\n")
        xml_fp.write(f"<step>{note_name[0]}</step>\n")
        if "#" in note_name:
            xml_fp.write("<alter>1</alter>\n")
        elif "b" in note_name:
            xml_fp.write("<alter>-1</alter>\n")
        xml_fp.write(f"<octave>{octave}</octave>\n")
        xml_fp.write("</pitch>\n")
        xml_fp.write(f"<duration>{note_to_value(duration, dotted)}</duration>\n")
        xml_fp.write(f"<voice>{voice}</voice>\n")
        xml_fp.write(f"<type>{duration}</type>\n")
        if dotted == True:
            xml_fp.write(f"<dot/>\n")
        xml_fp.write(f"<staff>{staff}</staff>\n")
        if (create_measure == True and tied == False): # or next_note[0] != "unknown":
            xml_fp.write("<notations>\n")
            xml_fp.write("<tied type=\"start\"/>\n")
            xml_fp.write("</notations>\n")
        elif create_measure == False and tied == True:
            xml_fp.write("<notations>\n")
            xml_fp.write("<tied type=\"stop\"/>\n")
            xml_fp.write("</notations>\n")
        elif create_measure == True and tied == True:
            xml_fp.write("<notations>\n")
            xml_fp.write("<tied type=\"stop\"/>\n")
            xml_fp.write("<tied type=\"start\"/>\n")
            xml_fp.write("</notations>\n")
        xml_fp.write("</note>\n")
        if create_measure == False and chord == False:
            beat += note_to_value(duration, dotted)

    return beat, create_measure, l1_note_buffer, l2_note_buffer, next_tied

def generate_rest(beat, create_measure, duration, dotted, time_sig_beats, l1_note_buffer, l2_note_buffer, xml_fp):
    # Generate and append MusicXML note entry
    # TODO add staff support
    # if duration == "unknown" or duration == "32nd" or (duration == "16th" and not dotted):
        #return beat, create_measure, l1_note_buffer, l2_note_buffer
    if duration != "unknown" and duration != "32nd" and (duration != "16th" or dotted):
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
            xml_fp.write("<note>\n")
            xml_fp.write("<rest/>\n")
            xml_fp.write(f"<duration>{note_to_value(duration, dotted)}</duration>\n")
            xml_fp.write(f"<type>{duration}</type>\n")
            if dotted == True:
                xml_fp.write(f"<dot/>\n")
            xml_fp.write("</note>\n")
            if create_measure == False:
                beat += note_to_value(duration, dotted)

    return beat, create_measure, l1_note_buffer, l2_note_buffer


def update_sheet(sheet, path, event):
    status, note, velocity, event_time = event
    print(f"Event: {event}")
    note = str(note) # make note number string for simplicity

    with open(path, "a") as xml_fp:
        # TODO thoroughly test pedal
        if status == 144 and velocity > 0:  # key pressed
            # Check if the pedal is pressed
            if sheet.pedal_pressed:
                sheet.notes_during_pedal = True
                # Check if there is a pedal markup to write
                if len(sheet.pedal_markup_buffer) > 0:
                    xml_fp.writelines(sheet.pedal_markup_buffer)
                    sheet.pedal_markup_buffer = []

            # starts at 0, then gets updated IN the loop
            sheet.note_start_times[note] = [event_time, sheet.beat, False] # record start time and amount of beats in measure (used by <backup>)
            sheet.dynamic = get_dynamic(velocity)
            print(f"Start time: {sheet.note_start_times[note][0]}, Start beat: {sheet.note_start_times[note][1]}, Dynamic: {sheet.dynamic}, Velocity: {velocity}")
            # rest is calculated by the current notes start time - the last notes end time

            # prevent chords from cloning rests
            if (sheet.last_note_end_time != 0 or sheet.last_note_start_time != 0) and sheet.last_note_start_time - sheet.note_start_times[note][0] < -((60 / sheet.bpm) / 8): #if this is not there, then it prints 0 when there is no rest
                if sheet.backup == True:
                    sheet.backup = False
                if sheet.chord == True:
                    sheet.chord = False

                # use the more recent number to generate a rest
                if sheet.last_note_start_time < sheet.last_note_end_time:
                    d = "{:.4f}".format(sheet.note_start_times[note][0] - sheet.last_note_end_time)
                    duration, dotted = get_note_duration(sheet.last_note_end_time, sheet.note_start_times[note][0], sheet.bpm)
                else:
                    d = "{:.4f}".format(sheet.note_start_times[note][0] - sheet.last_note_start_time)
                    duration, dotted = get_note_duration(sheet.last_note_start_time, sheet.note_start_times[note][0], sheet.bpm)

                print(f"Rest Time: {duration}, Dotted: {dotted}, Exact Duration: {d} seconds")

                if duration != "unknown":
                    sheet.beat, sheet.create_measure, sheet.l1_note_buffer, sheet.l2_note_buffer = generate_rest(sheet.beat, sheet.create_measure, duration, dotted, sheet.time_sig_beats, sheet.l1_note_buffer, sheet.l2_note_buffer, xml_fp)
                    
                    sheet.note_start_times[note] = [sheet.note_start_times[note][0], sheet.beat, False] # update starting beat for note
                    print(f"Updated start beat: {sheet.note_start_times[note][1]}")
            
            sheet.last_note_start_time = sheet.note_start_times[note][0] # record start time for next note

        elif (status == 128) or (status == 144 and velocity == 0): # key released
            if note in sheet.note_start_times:
                start_time, start_beat, tied = sheet.note_start_times.pop(note, None)
                end_time = event_time
                d = "{:.4f}".format(abs(start_time-end_time)) # we cut off the time at 3 decimals
                duration, dotted = get_note_duration(start_time, end_time, sheet.bpm)
                note_name = get_note(int(note), sheet.note_names)
                octave = get_octave(int(note))
                staff = get_staff(octave)

                print(f"Previous_note: {sheet.previous_note}")
                if (sheet.previous_note[0] != None and sheet.previous_note[0] - start_time > -((60 / sheet.bpm) / 8)
                    and sheet.previous_note[1] == duration and sheet.previous_note[2] == dotted
                    and duration != "unknown"):
                    sheet.chord = True
                    voice = sheet.previous_note[3]
                else:
                    sheet.chord = False
                    # sheet.voice += 1
                    voice = 1

                if start_beat != sheet.beat and duration != "unknown" and sheet.backup == True and sheet.chord == False:
                    # end backup
                    print(f"Start beat: {start_beat} != Beat: {sheet.beat}, Ending Backup..")
                    sheet.backup = False

                if start_beat < sheet.beat and duration != "unknown" and sheet.chord == False and sheet.backup != True:
                    print(f"Start beat: {start_beat} < Beat: {sheet.beat}, Writing backup: {sheet.beat - start_beat}")
                    write_backup(sheet.beat - start_beat, xml_fp)
                    sheet.beat = start_beat
                    sheet.backup = True
                    sheet.backup_voice += 1
                    voice = sheet.backup_voice
                
                sheet.previous_note = [start_time, duration, dotted, voice] # record for next note

                print (f"Note: {note_name}, Octave: {octave}, Duration: {duration}, Dotted: {dotted}, Exact Duration: {d} seconds, Chord: {sheet.chord}")
                sheet.last_note_end_time = event_time # update the last_note_end_time to be when the key is released

                if duration != "unknown":
                    if sheet.last_dynamic != sheet.dynamic and sheet.backup == False:
                        generate_dynamic(sheet.dynamic, staff, xml_fp)
                        sheet.last_dynamic = sheet.dynamic

                    sheet.beat, sheet.create_measure, sheet.l1_note_buffer, sheet.l2_note_buffer, tied = generate_note(sheet.beat, sheet.create_measure, duration, note_name, octave, sheet.chord, voice, dotted, staff, sheet.time_sig_beats, sheet.l1_note_buffer, sheet.l2_note_buffer, tied, xml_fp)
                    print(f"beat: {sheet.beat} measure: {sheet.measure}")

        elif status == 176 and note == "64":
            if velocity == 64:  # pedal pressed
                sheet.pedal_pressed = True
                sheet.notes_during_pedal = False # TODO test if this can be moved inside 'elif velocity == 0:'
                sheet.pedal_markup_buffer = ["<direction>\n", "<direction-type>\n", "<pedal type=\"start\" line=\"yes\"/>\n", "</direction-type>\n", "</direction>\n"]

            elif velocity == 0: # pedal released
                sheet.pedal_pressed = False
                # Check if notes were played while pressing the pedal
                if sheet.notes_during_pedal:
                    # Check if the pedal start markup needs to be written
                    if len(sheet.pedal_markup_buffer) > 0:
                        xml_fp.writelines(sheet.pedal_markup_buffer)
                    xml_fp.writelines(["<direction>\n", "<direction-type>\n", "<pedal type=\"stop\" line=\"yes\"/>\n", "</direction-type>\n", "</direction>\n"])
                sheet.pedal_markup_buffer = []
                
        if sheet.create_measure == True:
            print("Creating new measure")
            new_beat = note_to_value(duration, dotted) - (sheet.time_sig_beats * 8 - sheet.beat) # record leftover from first note
            sheet.beat = sheet.time_sig_beats * 8
            sheet.backup = False
            print(f"Beat: {sheet.beat}.. Interating through notes")
            for note in sheet.note_start_times:
                # TODO generate unique voices for each non-chord note
                # TODO thoroughly test
                start_time, start_beat, tied = sheet.note_start_times[note]
                end_time = event_time
                d = "{:.4f}".format(abs(start_time-end_time)) # we cut off the time at 3 decimals
                duration, dotted = get_note_duration(start_time, end_time, sheet.bpm)
                note_name = get_note(int(note), sheet.note_names)
                octave = get_octave(int(note))
                staff = get_staff(octave)

                print(f"Previous_note: {sheet.previous_note}")
                if (sheet.previous_note[0] != None and sheet.previous_note[0] - start_time > -((60 / sheet.bpm) / 8)
                    and sheet.previous_note[1] == duration and sheet.previous_note[2] == dotted
                    and duration != "unknown"):
                    sheet.chord = True
                    voice = sheet.previous_note[3]

                    # special condition when chord creates new measure
                    if start_beat < sheet.beat and duration != "unknown":
                        print(f"Start beat: {start_beat} < Beat: {sheet.beat} and Chord: True, New beat: {start_beat}")
                        sheet.beat = start_beat
                        sheet.backup = True # true, but no backup is written
                else:
                    sheet.chord = False
                    # sheet.voice += 1
                    voice = 1

                # might need to change to start_beat > sheet.beat
                if start_beat != sheet.beat and duration != "unknown" and sheet.backup == True and sheet.chord == False:
                    # end backup
                    print(f"Start beat: {start_beat} != Beat: {sheet.beat}, Ending Backup.. New beat: {sheet.after_backup_beat}")
                    sheet.beat = sheet.after_backup_beat
                    sheet.backup = False

                if start_beat < sheet.beat and duration != "unknown" and sheet.chord == False and sheet.backup != True:
                    print(f"Start beat: {start_beat} < Beat: {sheet.beat}, Writing backup: {sheet.beat - start_beat}")
                    write_backup(sheet.beat - start_beat, xml_fp)
                    # used when a note is supposed to be apart of a chord but other note get written in between them
                    if note_to_value(duration, dotted) + start_beat > sheet.time_sig_beats * 8 and new_beat > 0:
                        # TODO test
                        # backup by l1
                        duration_1, dotted_1 = get_closest_note(new_beat)
                        sheet.l1_note_buffer.append("<backup>\n")
                        sheet.l1_note_buffer.append(f"<duration>{note_to_value(duration_1, dotted_1)}</duration>\n")
                        sheet.l1_note_buffer.append("</backup>\n")
                        if new_beat - note_to_value(duration_1, dotted_1) > 0:
                            # backup by l2
                            duration_2, dotted_2 = get_closest_note(new_beat - note_to_value(duration_1, dotted_1))
                            sheet.l2_note_buffer.append("<backup>\n")
                            sheet.l2_note_buffer.append(f"<duration>{note_to_value(duration_2, dotted_2)}</duration>\n")
                            sheet.l2_note_buffer.append("</backup>\n")
                    sheet.beat = start_beat
                    sheet.backup = True
                    sheet.backup_voice += 1
                    voice = sheet.backup_voice
                
                sheet.previous_note = [start_time, duration, dotted, voice] # record for next note

                print (f"Note: {note_name}, Octave: {octave}, Duration: {duration}, Dotted: {dotted}, Exact Duration: {d} seconds, Chord: {sheet.chord}")
                sheet.last_note_end_time = event_time # update the last_note_end_time to be when the key is released

                if duration != "unknown":
                    if sheet.last_dynamic != sheet.dynamic and sheet.backup == False:
                        generate_dynamic(sheet.dynamic, staff, xml_fp)
                        sheet.last_dynamic = sheet.dynamic

                    sheet.beat, sheet.create_measure, sheet.l1_note_buffer, sheet.l2_note_buffer, tied = generate_note(sheet.beat, sheet.create_measure, duration, note_name, octave, sheet.chord, voice, dotted, staff, sheet.time_sig_beats, sheet.l1_note_buffer, sheet.l2_note_buffer, tied, xml_fp)
                    print(f"beat: {sheet.beat} measure: {sheet.measure}")

                # push copy of note back onto sheet.note_start_times
                leftover = note_to_value(duration, dotted) - (sheet.time_sig_beats * 8 - sheet.beat)
                if leftover < 0: # when note duration is 0
                    leftover = 0
                if leftover > new_beat:
                    new_beat = leftover
                if duration != "unknown":
                    sheet.buffer_note_start_times[note] = (event_time, leftover, tied)
                else:
                    sheet.buffer_note_start_times[note] = (event_time, new_beat, tied)

                if sheet.backup == True:
                    sheet.after_backup_beat = sheet.beat + note_to_value(duration, dotted)
                    sheet.beat = sheet.time_sig_beats * 8 # TODO test
            # end of for each loop
            print("Finished iterating through notes")

            if sheet.backup == True:
                sheet.backup = False
            if sheet.chord == True:
                sheet.chord = False
            
            # write the new measure
            sheet.measure += 1
            xml_fp.write("</measure>\n")
            xml_fp.write(f"<measure number=\"{sheet.measure}\">\n")
            xml_fp.writelines(sheet.l1_note_buffer)
            xml_fp.writelines(sheet.l2_note_buffer)
            sheet.create_measure = False
            sheet.beat = new_beat
            sheet.l1_note_buffer = [] # clear buffer
            sheet.l2_note_buffer = [] # clear buffer
            sheet.note_start_times = sheet.buffer_note_start_times
            sheet.buffer_note_start_times = {} # clear buffer dict
            sheet.after_backup_beat = 32
            # sheet.backup_voice = 1

    # write to json file
    return sheet