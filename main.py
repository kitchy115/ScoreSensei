import numpy as np
import pyaudio
import keyboard
import time
import json
import os

# 4th octive frequencies and notes
note_frequencies = {
    'C': 261.63,
    'D': 293.66,
    'E': 329.63,
    'F': 349.23,
    'G': 392.00,
    'A': 440.00,
    'B': 493.88
}

frequency_tolerance = 13  # e.g. A = 440 Hz so if it falls in range of 430 Hz - 450 Hz it will be detected as A assuming the frequency tolerance is 10 Hz

p = pyaudio.PyAudio()

FORMAT = pyaudio.paFloat32  # Set format to float32
CHANNELS = 1  # 1 For mono, 2 for stereo
RATE = 44100  # Sampling rate of 44100 Hz
CHUNK = 2048  # Number of audio samples per buffer

last_detection_time = 0
detection_interval = 0.5  # Minimum interval between detections

stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

def calibrate_notes(stream, note_frequencies):
    calibration_data = {}
    print("Starting calibration...")

    # Iterate over each note to calibrate the system
    for note in note_frequencies.keys():
        print(f"Please play the {note} note.")
        peak_magnitudes = []
        start_time = time.time()
        
        # Record for 5 seconds
        while time.time() - start_time < 5:
            data = np.frombuffer(stream.read(CHUNK, exception_on_overflow=False), dtype=np.float32)
            windowed_data = data * np.hanning(len(data)) # Apply a hanning window to the data
            fft_result = np.fft.fft(windowed_data) # Apply FFT to find the frequencies in the data
            magnitudes = np.abs(fft_result)
            peak_magnitude = np.max(magnitudes)
            peak_magnitudes.append(peak_magnitude)

        calibrated_magnitude = max(peak_magnitudes)  # Use the max peak magnitude for calibration
        calibration_data[note] = calibrated_magnitude  # Store in calibration data
        print(f"Calibrated {note} with peak magnitude: {calibrated_magnitude:.2f}")

    # Save calibration data to a JSON file
    with open("note_calibration.json", 'w') as f:
        json.dump(calibration_data, f)

    print("Calibration completed.")

# Load calibration data from file
def load_calibration():
    with open("note_calibration.json", 'r') as f:
        return json.load(f)

def detect_note(frequency, magnitude, calibration_data):
    global last_detection_time
    current_time = time.time()

    # Skip detection if the time from the last detected note is less than the set interval
    if current_time - last_detection_time < detection_interval:
        return None

    # Iterate over each note to check if the frequency is within the tolerance range
    for note, freq in note_frequencies.items():
        if freq - frequency_tolerance <= frequency <= freq + frequency_tolerance:

            # Check if magnitude meets calibrated threshold (80% of the max magnitude)
            if magnitude >= calibration_data[note] * 0.8: 
                last_detection_time = current_time
                return note
    return "Silence"

# Check if the calibration file exists, if not, start the calibration process
calibration_file = "calibration.json"
if not os.path.exists(calibration_file):
    print("Calibration file not found. Starting calibration process...")
    calibrate_notes(stream, note_frequencies)
    
calibration_data = load_calibration()

print("Listening for notes. Press 'q' to quit.")
try:
    while True:
        if keyboard.is_pressed('q'):
            break

        # Read data from the audio stream
        data = np.frombuffer(stream.read(CHUNK, exception_on_overflow=False), dtype=np.float32)
        windowed_data = data * np.hanning(len(data)) # Apply a hanning window to the data
        fft_result = np.fft.fft(windowed_data) # Apply FFT to find the frequencies in the data 
        frequencies = np.fft.fftfreq(len(fft_result), d=1./RATE)
        magnitudes = np.abs(fft_result)
        index = np.argmax(magnitudes)
        peak_frequency = abs(frequencies[index])
        peak_magnitude = magnitudes[index]

        # Detect note based on peak frequency and magnitude
        note = detect_note(peak_frequency, peak_magnitude, calibration_data)
        if note and note != "Silence":
            print(f"Detected Note: {note}")

except KeyboardInterrupt:
    print("Stopping...")
finally:
    stream.stop_stream()  # Stop the audio stream
    stream.close()  # Close the audio stream
    p.terminate()  # Terminate PyAudio session