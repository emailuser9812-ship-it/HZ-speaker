import sys, json, numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import pyaudio
import matplotlib.pyplot as plt

class ToneGenerator(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Advanced Python Tone Generator")
        self.setGeometry(200, 200, 600, 450)

        self.frequency = 440
        self.volume = 0.5
        self.running = False
        self.wave_type = "sine"

        layout = QVBoxLayout()

        # --- Frequency Slider ---
        self.freq_slider = QSlider(Qt.Horizontal)
        self.freq_slider.setRange(1, 300000)
        self.freq_slider.setValue(440)
        self.freq_slider.valueChanged.connect(self.update_frequency)

        self.freq_label = QLabel("Frequency: 440 Hz")

        # --- Volume Slider ---
        self.vol_slider = QSlider(Qt.Horizontal)
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(50)
        self.vol_slider.valueChanged.connect(self.update_volume)

        self.vol_label = QLabel("Volume: 50%")

        # --- Wave Selector ---
        self.wave_box = QComboBox()
        self.wave_box.addItems(["sine", "square", "triangle", "sawtooth"])
        self.wave_box.currentTextChanged.connect(self.update_wave_type)

        # --- Buttons ---
        self.start_btn = QPushButton("START")
        self.start_btn.clicked.connect(self.start_sound)

        self.stop_btn = QPushButton("STOP")
        self.stop_btn.clicked.connect(self.stop_sound)

        self.save_btn = QPushButton("Save Preset")
        self.save_btn.clicked.connect(self.save_preset)

        self.load_btn = QPushButton("Load Preset")
        self.load_btn.clicked.connect(self.load_preset)

        # --- Add items ---
        layout.addWidget(QLabel("Wave Type:"))
        layout.addWidget(self.wave_box)
        layout.addWidget(self.freq_label)
        layout.addWidget(self.freq_slider)
        layout.addWidget(self.vol_label)
        layout.addWidget(self.vol_slider)
        layout.addWidget(self.start_btn)
        layout.addWidget(self.stop_btn)
        layout.addWidget(self.save_btn)
        layout.addWidget(self.load_btn)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Audio setup
        self.audio = pyaudio.PyAudio()

    def update_frequency(self, v):
        self.frequency = v
        self.freq_label.setText(f"Frequency: {v} Hz")

    def update_volume(self, v):
        self.volume = v / 100
        self.vol_label.setText(f"Volume: {v}%")

    def update_wave_type(self, t):
        self.wave_type = t

    def generate_wave(self, frames):
        t = np.linspace(0, frames/44100, frames)

        if self.wave_type == "sine":
            wave = np.sin(2 * np.pi * self.frequency * t)
        elif self.wave_type == "square":
            wave = np.sign(np.sin(2*np.pi*self.frequency*t))
        elif self.wave_type == "triangle":
            wave = 2 * np.abs(2*((t*self.frequency)-np.floor(0.5+(t*self.frequency)))) - 1
        elif self.wave_type == "sawtooth":
            wave = 2*(t*self.frequency - np.floor(0.5 + t*self.frequency))

        return (wave * self.volume).astype(np.float32)

    def audio_callback(self, in_data, frame_count, time_info, status):
        data = self.generate_wave(frame_count)
        return (data.tobytes(), pyaudio.paContinue)

    def start_sound(self):
        if self.running:
            return

        self.running = True
        self.stream = self.audio.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=44100,
            output=True,
            stream_callback=self.audio_callback
        )
        self.stream.start_stream()

    def stop_sound(self):
        if not self.running:
            return

        self.running = False
        self.stream.stop_stream()
        self.stream.close()

    def save_preset(self):
        preset = {
            "frequency": self.frequency,
            "volume": self.volume,
            "wave": self.wave_type
        }
        with open("preset.json", "w") as f:
            json.dump(preset, f)

        QMessageBox.information(self, "Saved", "Preset saved!")

    def load_preset(self):
        try:
            with open("preset.json", "r") as f:
                data = json.load(f)

            self.frequency = data["frequency"]
            self.volume = data["volume"]
            self.wave_type = data["wave"]

            self.freq_slider.setValue(self.frequency)
            self.vol_slider.setValue(int(self.volume * 100))
            self.wave_box.setCurrentText(self.wave_type)

            QMessageBox.information(self, "Loaded", "Preset loaded!")

        except FileNotFoundError:
            QMessageBox.warning(self, "Error", "preset.json not found!")

app = QApplication(sys.argv)
win = ToneGenerator()
win.show()
sys.exit(app.exec_())
