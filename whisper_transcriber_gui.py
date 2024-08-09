import pyaudio
import wave
import threading
import os
import whisper
import warnings
import pyautogui
import flet as ft
import pygame
import keyboard
import time

# Suppress specific UserWarning
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

class VoiceRecorderApp:
    def __init__(self):
        self.audio_filename = "recording.wav"
        self.transcription_model = "base"
        self.recording = False
        self.transcribing = False
        self.audio_folder = "recordings"
        self.audio = None
        self.stream = None
        self.frames = []
        self.start_stop_button = None
        self.transcription_box = None
        self.transcribing_indicator = None  # For the loading indicator
        self.transcribing_text = None  # For the text next to the loading indicator
        self.window_visible = False
        self.last_activity_time = time.time()

        if not os.path.exists(self.audio_folder):
            os.makedirs(self.audio_folder)

        pygame.mixer.init()

        # Set up the keyboard shortcuts
        keyboard.add_hotkey('win+j', self.toggle_visibility_and_recording)
        keyboard.add_hotkey('win+x', self.cancel_recording)

    def setup_audio(self):
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=pyaudio.paInt16,
                                      channels=1,
                                      rate=44100,
                                      input=True,
                                      frames_per_buffer=1024)

    def record_audio(self):
        while self.recording:
            data = self.stream.read(1024)
            self.frames.append(data)

        with wave.open(os.path.join(self.audio_folder, self.audio_filename), 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(44100)
            wf.writeframes(b''.join(self.frames))

        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

    def toggle_visibility_and_recording(self, e=None):
        self.last_activity_time = time.time()  # Update the activity time
        if not self.window_visible:
            self.toggle_recording()
            self.window_visible = True
            self.page.window_visible = True
            self.page.update()
        else:
            self.toggle_recording()

    def toggle_recording(self, e=None):  # Made e optional to allow shortcut use
        self.last_activity_time = time.time()  # Update the activity time
        if not self.recording:
            self.transcribing = False
            self.recording = True
            self.frames = []
            self.setup_audio()
            threading.Thread(target=self.record_audio).start()
            if self.start_stop_button:
                self.start_stop_button.text = "Stop Recording"
            pygame.mixer.music.load('starting_audio.mp3')
            pygame.mixer.music.play()
        else:
            self.recording = False
            if self.start_stop_button:
                self.start_stop_button.text = "Start Recording"
            pygame.mixer.music.load('ending_audio.mp3')
            pygame.mixer.music.play()
            self.start_transcription_ui()
            threading.Thread(target=self.transcribe_audio).start()

        if self.start_stop_button:
            self.start_stop_button.update()

    def cancel_recording(self, e=None):
        self.last_activity_time = time.time()  # Update the activity time
        if self.recording:
            self.recording = False
            self.frames = []  # Clear the recorded frames
            if self.start_stop_button:
                self.start_stop_button.text = "Start Recording"
            pygame.mixer.music.load('ending_audio.mp3')
            pygame.mixer.music.play()

            # Hide transcription UI if it was shown
            self.end_transcription_ui()

        if self.start_stop_button:
            self.start_stop_button.update()

    def start_transcription_ui(self):
        self.transcribing = True
        if self.start_stop_button:
            self.start_stop_button.visible = False
        self.transcribing_indicator.visible = True
        self.transcribing_text.visible = True
        self.transcribing_indicator.update()
        self.transcribing_text.update()

    def end_transcription_ui(self):
        self.transcribing = False
        if self.start_stop_button:
            self.start_stop_button.visible = True
        self.transcribing_indicator.visible = False
        self.transcribing_text.visible = False
        if self.start_stop_button:
            self.start_stop_button.update()
        self.transcribing_indicator.update()
        self.transcribing_text.update()

    def transcribe_audio(self):
        model = whisper.load_model(self.transcription_model)
        result = model.transcribe(os.path.join(self.audio_folder, self.audio_filename))
        transcription_text = result['text']
        self.transcription_box.value = transcription_text
        self.transcription_box.update()
        pyautogui.write(transcription_text)
        self.end_transcription_ui()

    def hide_if_idle(self):
        while True:
            if self.window_visible and (time.time() - self.last_activity_time > 60):
                self.window_visible = False
                self.page.window_visible = False
                self.page.update()
            time.sleep(1)

    def main(self, page: ft.Page):
        self.page = page
        page.title = "Voice Recorder with Transcription"
        page.window_height = 200
        page.window_width = 300
        text_field_width = 0.9 * page.window_width
        text_field_height = 200
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.window_always_on_top = True  # Keep the window always on top
        page.window_visible = True  # Start with the window hidden

        self.start_stop_button = ft.ElevatedButton(
            text="Start Recording",
            on_click=self.toggle_recording
        )
        self.start_stop_button = ft.IconButton(
            icon= ft.icons.MIC_ROUNDED,
            on_click=self.toggle_recording,
            icon_size=0.1 * page.height
        )

        self.transcribing_indicator = ft.ProgressRing(visible=False)
        self.transcribing_text = ft.Text("Transcribing...", visible=False)

        self.transcription_box = ft.TextField(
            label="Transcription",
            multiline=True,
            read_only=True,
            width=text_field_width,
            height=text_field_height,
        )

        page.add(
            ft.Column(
                [
                    self.start_stop_button,
                    ft.Row(
                        [self.transcribing_indicator, self.transcribing_text],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )


        threading.Thread(target=self.hide_if_idle, daemon=True).start()

# Run the FLET app
if __name__ == "__main__":
    app = VoiceRecorderApp()
    ft.app(target=app.main)

