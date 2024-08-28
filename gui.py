import os
import whisper
import numpy as np
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QApplication, QTextEdit, QPushButton, QComboBox
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QThread, pyqtSignal
import pyqtgraph as pg
from pydub import AudioSegment
from pytube import YouTube

# Import the generated UI and resources files
import whisperGUI  # This is the generated .py file from the .ui file
import resources_rc  # This is the generated .py file from the .qrc file

class WallakAtaApp(QMainWindow, whisperGUI.Ui_MainWindow):
    def __init__(self):
        super(WallakAtaApp, self).__init__()
        # Set up the UI
        self.setupUi(self)

        # Initialize Whisper model
        self.whisper_model = whisper.load_model("medium")

        # Set up the plot widget and curve
        self.curve = self.plot_widget.plot()  # Initialize the curve object

        # Connect buttons to their respective actions
        self.utube_transcribe_2.clicked.connect(self.transcribe_audio_action)
        self.whisper_file_upload.clicked.connect(self.upload_file_action)

        # Ensure pydub can find ffmpeg (for specific formats)
        AudioSegment.converter = r"C:\Users\Grillex\PycharmProjects\realtime-whisper\ffmpeg.exe"

    def transcribe_audio_action(self):
        # Get the YouTube URL from the text edit
        youtube_url = self.utube_url_2.toPlainText().strip()
        if youtube_url:
            self.download_and_transcribe_youtube_audio(youtube_url)

    def upload_file_action(self):
        # Open a file dialog to select an audio file
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Audio File", "", "Audio Files (*.wav *.mp3 *.m4a *.aac *.flac)")
        if file_path:
            self.transcribe_audio_file(file_path)

    def transcribe_audio_file(self, file_path):
        self.openai_worker = OpenAIWorker(file_path=file_path)
        self.openai_worker.data_ready.connect(self.handle_transcription_result)
        self.openai_worker.start()

    def handle_transcription_result(self, transcript):
        # Display the transcription result in the UI
        self.STT_output.setHtml(transcript)  # Assuming `stt_output` is a QWebEngineView


class OpenAIWorker(QThread):
    data_ready = pyqtSignal(str)

    def __init__(self, file_path=None):
        super(OpenAIWorker, self).__init__()
        self.file_path = file_path
        self.whisper_model = whisper.load_model("medium")

    def run(self):
        if self.file_path:
            self.local_whisper_transcribe(self.file_path)

    def local_whisper_transcribe(self, file_path):
        try:
            # Load audio using the custom method
            audio_data = self.load_audio_custom(file_path)
            result = self.whisper_model.transcribe(audio_data)
            self.data_ready.emit(result["text"])
        except Exception as e:
            import traceback
            error_message = traceback.format_exc()
            self.data_ready.emit(f"Error during transcription: {error_message}")

    def load_audio_custom(self, file_path):
        # Load the audio file using pydub
        audio = AudioSegment.from_file(file_path)
        # Convert to mono and set frame rate to 16000
        audio = audio.set_channels(1).set_frame_rate(16000)
        # Convert to numpy array
        samples = np.array(audio.get_array_of_samples()).astype(np.float32) / 32768.0
        return samples


if __name__ == "__main__":
    app = QApplication([])
    window = WallakAtaApp()
    window.show()
    app.exec_()
