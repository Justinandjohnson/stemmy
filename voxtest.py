import sys
import numpy as np
import sounddevice as sd
import tempfile
import soundfile as sf
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QComboBox, QProgressBar, QFileDialog
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtGui import QPixmap, QPalette, QBrush
from PyQt5.QtCore import Qt, QUrl, QThread, pyqtSignal, QTimer
import shutil
import os
import torch
import torchaudio
import torch.hub

class AudioRecorder(QThread):
    finished = pyqtSignal(np.ndarray, int)  
    audio_level_updated = pyqtSignal(float) 

    def __init__(self, fs, channels, device=None):
        super().__init__()
        self.fs = fs
        self.channels = channels
        self.device = device
        self.recording = False
        self.recorded_audio = np.empty((0, channels), np.float32)

    def run(self):
        self.recording = True
        with sd.InputStream(samplerate=self.fs, channels=self.channels, device=self.device, callback=self.audio_callback):
            while self.recording:
                sd.sleep(100)
        self.finished.emit(self.recorded_audio, self.fs)

    def audio_callback(self, indata, frames, time, status):
        self.recorded_audio = np.vstack((self.recorded_audio, indata))
        audio_level = np.sqrt(np.mean(indata**2))
        self.audio_level_updated.emit(audio_level * 100)  # Amplify 

    def stop(self):
        self.recording = False

class DemucsAudioApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Demucs Vocal Isolation App")
        self.setGeometry(100, 100, 500, 550)
        self.layout = QVBoxLayout()
        self.init_background()

        # Load Demucs model with GPU support if available
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.demucs = torch.hub.load('facebookresearch/demucs', 'demucs', model_name='demucs_extra', device=self.device)

        self.player = QMediaPlayer()
        self.deviceComboBox = QComboBox()
        self.populate_device_list()
        self.audioLevelProgressBar = QProgressBar()
        self.audioLevelProgressBar.setMaximum(100)
        self.stemmingProgressBar = QProgressBar()
        self.stemmingProgressBar.setMaximum(100)
        self.playButton = QPushButton('Play Beat')
        self.recordButton = QPushButton('Start Recording')
        self.isolateButton = QPushButton('Isolate Vocals')
        self.uploadButton = QPushButton('Upload Recording')
        self.saveStemsButton = QPushButton('Save Separated Stems')

        self.setupLayout()
        self.fs = 44100
        self.recorder = None
        self.temp_file_path = None
        self.output_path = None

    def setupLayout(self):
        self.layout.addWidget(self.deviceComboBox)
        self.layout.addWidget(self.audioLevelProgressBar)
        self.layout.addWidget(self.stemmingProgressBar)
        self.layout.addWidget(self.playButton)
        self.layout.addWidget(self.recordButton)
        self.layout.addWidget(self.isolateButton)
        self.layout.addWidget(self.uploadButton)
        self.layout.addWidget(self.saveStemsButton)
        self.setLayout(self.layout)

        self.playButton.clicked.connect(self.toggle_playback)
        self.recordButton.clicked.connect(self.toggle_recording)
        self.isolateButton.clicked.connect(self.isolate_vocals)
        self.uploadButton.clicked.connect(self.upload_recording)
        self.saveStemsButton.clicked.connect(self.save_stems)

    def init_background(self):
        backgroundImage = QPixmap("bgs.jpg")
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(backgroundImage.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

    def populate_device_list(self):
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                self.deviceComboBox.addItem(device['name'], userData=i)

    def toggle_playback(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
            self.playButton.setText('Play Beat')
        else:
            url = QUrl.fromLocalFile(os.path.abspath("londonbeachesx.wav"))
            content = QMediaContent(url)
            self.player.setMedia(content)
            self.player.play()
            self.playButton.setText('Pause Beat')

    def toggle_recording(self):
        if self.recorder and self.recorder.isRunning():
            self.recorder.stop()
            self.recordButton.setText('Start Recording')
            self.recorder.audio_level_updated.disconnect(self.update_audio_level)
        else:
            self.recordButton.setText('Stop Recording')
            device_index = self.deviceComboBox.currentData()
            self.recorder = AudioRecorder(self.fs, 2, device=device_index)
            self.recorder.finished.connect(self.save_recording)
            self.recorder.audio_level_updated.connect(self.update_audio_level)
            self.recorder.start()

    def upload_recording(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Recording", "", "Audio Files (*.mp3 *.wav *.flac)")
        if file_name:
            self.temp_file_path = file_name
            print(f"Selected file for processing: {self.temp_file_path}")

    def save_recording(self, audio_data, fs):
        self.temp_file_path = tempfile.mktemp(prefix='recorded_', suffix='.wav', dir='.')
        sf.write(self.temp_file_path, audio_data, fs)
        print(f"Recording saved to {self.temp_file_path}")

    def update_audio_level(self, level):
        self.audioLevelProgressBar.setValue(int(level))

    def isolate_vocals(self):
        self.start_stemming_progress()
        if self.temp_file_path:
            output_directory = './output'
            # Ensure output directory exists
            os.makedirs(output_directory, exist_ok=True)
            self.output_path = os.path.join(output_directory, os.path.basename(self.temp_file_path).replace('.wav', '_vocals.wav'))

            waveform, sample_rate = torchaudio.load(self.temp_file_path)
            waveform = waveform.to(self.device)

            # Separate sources
            with torch.no_grad():
                separated = self.demucs.separate(waveform[None, ...])[0]

            # Assuming index 0 is vocals for Demucs output
            vocals = separated[0].cpu()

            # Save the vocals track
            torchaudio.save(self.output_path, vocals, sample_rate)
            print(f"Vocals isolated and saved to {self.output_path}")
        self.stop_stemming_progress()

    def start_stemming_progress(self):
        self.stemmingProgressBar.setValue(50)  # Simulate progress

    def stop_stemming_progress(self):
        self.stemmingProgressBar.setValue(100) 

    def save_stems(self):
        if self.output_path:
            save_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Audio Files (*.wav)")
            if save_path:
                shutil.copy(self.output_path, save_path)
                print(f"Stems saved to {save_path}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DemucsAudioApp()
    window.show()
    sys.exit(app.exec_())
