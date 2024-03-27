from pygame import midi
import keyboard
import time

midi.init()

midi_input = midi.Input(midi.get_default_input_id())

def get_note(note_number):
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    return note_names[note_number % 12]

def get_octave(note_number):
    return (note_number // 12) - 1  # // = truncating division

threshold = 0.1

end_time = None

try:
    print('*** Ready to play ***')
    print('**Press [q] to quit**')

    while not keyboard.is_pressed('q'):
        
        # Detect keypress on input
        if midi_input.poll():
            
            # Get MIDI event information
            midi_events = midi_input.read(1000)

            for event in midi_events:
                data, timestamp = event[0], event[1]
                status, note, velocity, _ = data
                
                if status == 144 and velocity > 0: # key pressed
                    current_time = time.time()

                    # If the previous note is finished playing
                    if end_time is not None:
                        elapsed_time = current_time - end_time

                        # If the elapsed time between the previous note and current note is under the threshold
                        if elapsed_time <= threshold:
                            print(f"Grace note detected: {get_note(note) + str(get_octave(note))}")

                elif (status == 128) or (status == 144 and velocity == 0): # key released
                    end_time = time.time()
                    
except KeyboardInterrupt:
    print("Exiting...")

finally:
    # Close the midi interface
    midi.quit()
