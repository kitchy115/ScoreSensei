from pygame import midi
import keyboard

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

note_ending = ["</pitch>\n",
               "<duration>1</duration>\n",
               "<type>quarter</type>\n",
               "</note>\n"]

beat = 0
measure = 1

def get_note(note_info):
    match note_info % 12:
        case 0:
            return "C"
        case 1:
            return "C#"
        case 2:
            return "D"
        case 3:
            return "D#"
        case 4:
            return "E"
        case 5:
            return "F"
        case 6:
            return "F#"
        case 7:
            return "G"
        case 8:
            return "G#"
        case 9: 
            return "A"
        case 10:
            return "A#"
        case 11:
            return "B"
        
def get_octave(note_info):
    return (note_info // 12) - 1 # // = truncating division

def generate(note, octave, beat, measure):
    with open("sheet.musicxml", "a") as file:
        # run until note array is empty
        # determine if measure is full
        if beat > 3: # create a new measure
            file.write("</measure>\n")
            measure += 1
            file.write("<measure number=\"" + str(measure) + "\">\n") # create a new measure
            beat = 0
        file.writelines(note_template) # add note_template
        file.write("<step>" + str(note[0]) + "</step>\n") # add the note information
        if len(note) > 1: # check if note is sharp/flat
            if note[1] == "#":
                file.write("<alter>1</alter>\n")
            else:
                file.write("<alter>-1</alter>\n")
        file.write("<octave>" + str(octave) + "</octave>\n")
        beat += 1
        file.writelines(note_ending) # write note_ending
    
    return beat, measure

midi.init()

# This prints the default device ids that we are outputting to / taking input from
print('Output ID', midi.get_default_output_id())
print('Input ID', midi.get_default_input_id())

# List the MIDI devices that can be used
for i in range(0, midi.get_count()):
    print(i, midi.get_device_info(i))

# Here, you must check what the device # for your MIDI controller is
# You will not be guaranteed that the MIDI controller you want to use is the default

# Start the input stream
input = midi.Input(midi.get_default_input_id())

# Here's an example of setting the input device to something other than the default
# input = midi.Input(3)

print('*** Ready to play ***')
print('**Press [q] to quit**')

with open("sheet.musicxml", "w") as file:
    file.writelines(template)

while keyboard.is_pressed('q') != True:
    # Detect keypress on input
    if input.poll():
        # Get MIDI event information
        event = input.read(1000)
        print(event)
        if event[0][0][0] == 144:
            print(get_note(event[0][0][1]), get_octave(event[0][0][1]))
            beat, measure = generate(get_note(event[0][0][1]), get_octave(event[0][0][1]), beat, measure)

# Close the midi interface
midi.quit()

# write template_ending
with open("sheet.musicxml", "a") as file:
    file.writelines(template_ending)