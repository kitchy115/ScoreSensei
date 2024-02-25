from pygame import midi
import keyboard

midi.init()

input_device = midi.Input(midi.get_default_input_id())

pedal_state = False
pressed_time = None

try:
    print('*** Ready to play ***')
    print('**Press [q] to quit**')

    while not keyboard.is_pressed('q'):
        # Detect keypress on input
        if input_device.poll():
            # Get MIDI event information
            midi_events = input_device.read(1000)

            for event in midi_events:
                data, timestamp = event[0], event[1]
                status, note, velocity, _ = data
                
                if status == 144 and velocity > 0: # key pressed
                    if velocity <= 29:
                        print(f"pianississimo {velocity}")
                    elif 30 <= velocity <= 39:
                        print(f"pianissimo {velocity}")
                    elif 40 <= velocity <= 49:
                        print(f"piano {velocity}")
                    elif 50 <= velocity <= 59:
                        print(f"mezzo-piano {velocity}")
                    elif 60 <= velocity <= 69:
                        print(f"mezzo-forte {velocity}")
                    elif 70 <= velocity <= 79:
                        print(f"forte {velocity}")
                    elif 80 <= velocity <= 89:
                        print(f"fortissimo {velocity}")
                    elif 90 <= velocity:
                        print(f"fortississimo {velocity}")
finally:
    # Close the midi interface
    midi.quit()