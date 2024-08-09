import pyaudio
import wave
import threading
import keyboard
import os
import whisper
import warnings
import pyautogui
import pygame

# Suppress specific UserWarning
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

# Variables
audio_filename = "recording.wav"
transcription_model = "base"
recording = False
audio_folder = "recordings"
audio = None
stream = None
frames = []

# Ensure the audio folder exists
if not os.path.exists(audio_folder):
    os.makedirs(audio_folder)

def setup_audio():
    global audio, stream
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=44100,
                        input=True,
                        frames_per_buffer=1024)

# Audio recording function
def record_audio():
    global recording, stream, frames

    print("Recording... Press Win + J to stop.")
    while recording:
        data = stream.read(1024)
        frames.append(data)

    print("Recording stopped.")
    # Save the recorded audio to a file
    with wave.open(os.path.join(audio_folder, audio_filename), 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b''.join(frames))

    # Terminate the stream and PyAudio instance
    stream.stop_stream()
    stream.close()
    audio.terminate()

# Function to start/stop recording
def toggle_recording():
    global recording, frames

    if not recording:
        recording = True
        frames = []
        setup_audio()
        threading.Thread(target=record_audio).start()
        pygame.mixer.music.load('starting_audio.mp3')
        pygame.mixer.music.play()
    else:
        recording = False
        pygame.mixer.music.load('ending_audio.mp3')
        pygame.mixer.music.play()
        transcribe_audio()

def transcribe_audio():
    print("Transcribing...")
    model = whisper.load_model(transcription_model)
    result = model.transcribe(os.path.join(audio_folder, audio_filename))
    transcription_text = result['text']
    print("Transcription:")
    print(transcription_text)

    # Type the transcription result into the active text field
    pyautogui.write(transcription_text)

pygame.mixer.init()

# Bind the shortcut to toggle recording
keyboard.add_hotkey('win+j', toggle_recording)

print("Script running... Press Win + J to start/stop recording.")

# Keep the script running indefinitely
keyboard.wait('esc')  # Press 'Esc' to exit the script if needed
