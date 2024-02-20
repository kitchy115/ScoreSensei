from pygame import midi
import keyboard
import time

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
                status, control, velocity, _ = data
                
                if 176 <= status <= 191 and control == 64: # Check for control change and sustain pedal messages
                    if velocity >= 64 and not pedal_state:  # pedal pressed
                        pedal_state = True
                        pressed_time = time.time()
                        print("Sustain Pressed")
                    elif velocity < 64 and pedal_state:  # pedal released
                        pedal_state = False
                        if pressed_time is not None:
                            duration = time.time() - pressed_time
                            print(f"Sustain Released. Duration: {duration:.2f} seconds")
                            pressed_time = None

finally:
    # Close the midi interface
    midi.quit()