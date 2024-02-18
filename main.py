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
        return "sixteenth"
    elif abs(THIRTY_SECOND_DURATION * error <= duration <= THIRTY_SECOND_DURATION / error):
        return "thirty-second"
    else:
        return "unknown"

note_start_times = {}
beat = 0
measure = 1


try:
    print('*** Ready to play ***')
    print('**Press [q] to quit**')

    with open("sheet.musicxml", "w") as file:
        file.writelines(template)

    last_note_end_time = 0 #when the last note ends

    while not keyboard.is_pressed('q'):
        # Detect keypress on input
        if input_device.poll():
            # Get MIDI even information
            midi_events = input_device.read(1000)
            
            for event in midi_events:
                data, timestamp = event[0], event[1]
                status, note, velocity, _ = data

                if status == 144 and velocity > 0:  # key pressed
                      # starts at 0, then gets updated IN the loop
                    note_start_times[note] = time.time()
                    #rest is calculated by the current notes start time - the last notes end time
                    if last_note_end_time != 0: #if this is not there, then it prints 0 when there is no rest
                        rest = "{:.4f}".format(note_start_times[note] - last_note_end_time)
                        print(f"Rest Time: {rest} seconds")


                elif (status == 128) or (status == 144 and velocity == 0):  # key released
                    if note in note_start_times:
                        start_time = note_start_times.pop(note, None)
                        end_time = time.time()
                        d = "{:.4f}".format(abs(start_time-end_time)) #we cut off the time at 3 decimals
                        duration = get_note_duration(start_time, end_time)
                        note_name = get_note(note)
                        octave = get_octave(note)

                        print (f"Note:{note_name}, Octave:{octave}, Duration:{duration}, Exact Duration:{d} seconds")
                        last_note_end_time = time.time() #update the last_note_end_time to be when the key is realirzed
                        
                        if duration != "unknown":
                            # Generate and append MusicXML note entry
                            with open("sheet.musicxml", "a") as file:
                                file.writelines(note_template)
                                file.write(f"<step>{note_name}</step>\n")
                                if "#" in note_name:
                                    file.write("<alter>1</alter>\n")
                                file.write(f"<octave>{octave}</octave>\n")
                                file.writelines(note_ending[duration])

finally:
    # Close the midi interface
    midi.quit()

    # write template_ending 
    with open("sheet.musicxml", "a") as file:
        file.writelines(template_ending)
