# Simple Piano Note Detector for One Octave

# This program was tested using a virtual piano available at virtualpiano.net focusing on the 4th octave.
# Ensure that all of the settings are set to default, except for the sustain option, that is disabled.
# Ensure that your device is setup to record sound from your virtual piano. (VB-Audio was used for testing)

## How to Calibrate

- You will be prompted to play each note starting from C to B. 
- You will have 5 seconds to play the note.
- The program will record the highest magnitude for each note.
- Once the terminal says "Calibration completed." and then "Listen for notes. Press 'q' to quit.', you can play around with the virtual piano.

## Usage Instructions

- Start the program and the calibration process will begin.
- Follow the instructions on the terminal.
- After the calibration process ends, play notes on your piano, and the program will detect and display them.
- Press 'q' to quit.

## Requirements

- Python 3.8.18
- numpy 1.24.3
- PyAudio 0.2.14
- keyboard 0.13.5