import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QAction, QVBoxLayout, QHBoxLayout,
    QSlider, QDial, QTableWidget, QTableWidgetItem, QLineEdit, QLabel,
    QSpinBox, QWidget, QFileDialog, QPushButton
)
from PyQt5.QtCore import Qt
from pyqtgraph import PlotWidget
import wave
import numpy as np
from scipy.io.wavfile import write
from scipy.io import wavfile
from equalizer import equalize
from echo import add_reverb
from distortion import apply_distortion


class AudioGUI(QMainWindow):

    def open_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open WAV File", "", "WAV Files (*.wav)", options=options)
        if file_path:
            self.table_update(file_path)
            if self.graphType == "A(t)":
                self.load_wave(file_path)
            elif self.graphType == "A(f)":
                self.load_wave_FFT(file_path)

    def save_audio(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Audio", "", "WAV (*.wav)")
        if file_path and hasattr(self, 'raw_audio_data') and hasattr(self, 'wav_params'):
            try:
                with wave.open(file_path, 'wb') as out_file:
                    out_file.setnchannels(1)
                    out_file.setsampwidth(2)
                    out_file.setframerate(self.wav_params.framerate)
                    out_file.writeframes(self.raw_audio_data.astype(np.int16).tobytes())
                print(f"Audio saved successfully to: {file_path}")
            except Exception as e:
                print(f"Save error: {e}")

    def table_update(self, file_path):
        import os
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)

        with wave.open(file_path, 'rb') as wav_file:
            n_frames = wav_file.getnframes()
            framerate = wav_file.getframerate()
            duration = n_frames / framerate

            data = wav_file.readframes(n_frames)
            wave_data = np.frombuffer(data, dtype=np.int16)

            max_amplitude = np.max(np.abs(wave_data))

        self.file_table.setItem(0, 0, QTableWidgetItem(file_name))
        self.file_table.setItem(0, 1, QTableWidgetItem(str(file_size)))
        self.file_table.setItem(0, 2, QTableWidgetItem(f"{duration:.2f}"))
        self.file_table.setItem(0, 3, QTableWidgetItem(f"{20 * np.log10(max_amplitude):.2f}"))

    def load_wave(self, file_path):
        if self.graphType == "A(t)":
            with wave.open(file_path, 'rb') as wav_file:
                self.wav_params = wav_file.getparams()
                n_channels = wav_file.getnchannels()
                sample_width = wav_file.getsampwidth()
                framerate = wav_file.getframerate()
                n_frames = wav_file.getnframes()

                data = wav_file.readframes(n_frames)
                wave_data = np.frombuffer(data, dtype=np.int16)

                if n_channels == 2:
                    wave_data = wave_data.reshape(-1, 2).mean(axis=1)

                duration = n_frames / framerate
                time = np.linspace(0, duration, num=len(wave_data))

                self.graph.clear()
                self.graph.plot(time, wave_data, pen='r')

                self.raw_audio_data = wave_data
                self.audio_file_path = file_path

    def load_wave_FFT(self, file_path):
        if self.graphType == "A(f)":
            with wave.open(file_path, 'rb') as wav_file:
                n_channels = wav_file.getnchannels()
                framerate = wav_file.getframerate()
                n_frames = wav_file.getnframes()

                data = wav_file.readframes(n_frames)
                wave_data = np.frombuffer(data, dtype=np.int16)

                wave_data = wave_data.reshape(-1, n_channels)
                channel_data = wave_data[:, 0]

                freqs = np.fft.rfftfreq(n_frames, 1 / framerate)
                fft_magnitudes = np.abs(np.fft.rfft(channel_data))

                self.graph.clear()
                self.graph.plot(freqs, fft_magnitudes, pen='b')

    def refresh_action(self):
        if hasattr(self, 'raw_audio_data') and hasattr(self, 'wav_params'):
            threshold_db = self.threshold_input.value()
            level = self.level_dial.value()
            gain_db = self.gain_input.value()

            treble = self.treble_slider.value()
            mid = self.mid_slider.value()
            bass = self.bass_slider.value()
            decay = self.decay_dial.value() / 10.0
            wetness = self.wetness_dial.value() / 10.0
            delay = self.delay_input.value()

            processed_audio = apply_distortion(self.raw_audio_data, threshold_db, level, gain_db)
            processed_audio = equalize(processed_audio, self.wav_params.framerate, treble, mid, bass)
            processed_audio = add_reverb(processed_audio, delay, decay, wetness)

            self.raw_audio_data = processed_audio
            duration = len(processed_audio) / self.wav_params.framerate
            time = np.linspace(0, duration, num=len(processed_audio))

            self.graph.clear()
            self.graph.plot(time, processed_audio, pen='r')

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audio GUI")
        self.graphType = "A(t)"

        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout_bottom = QHBoxLayout()

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_file)
        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_audio)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)

        graph_menu = menu_bar.addMenu("Graph")
        at_action = QAction("A(t)", self)
        af_action = QAction("A(f)", self)
        at_action.triggered.connect(self.at_action_graph)
        af_action.triggered.connect(self.af_action_graph)
        graph_menu.addAction(at_action)
        graph_menu.addAction(af_action)

        self.graph = PlotWidget()
        main_layout.addWidget(self.graph)

        controls_layout = QHBoxLayout()
        TbRf_layout = QVBoxLayout()
        controlsEqRv_layout = QHBoxLayout()
        controlsThGn_layout = QHBoxLayout()
        main_controls_layout = QVBoxLayout()

        Th_layout = QVBoxLayout()
        Gn_layout = QVBoxLayout()
        Dl_layout = QVBoxLayout()

        self.empty_space0 = self.create_dial("", controlsEqRv_layout)
        self.empty_space0.hide()

        self.treble_slider = self.create_slider("Treble", controlsEqRv_layout)
        self.treble_slider.setValue(100)
        self.treble_slider.setRange(50, 150)

        self.empty_space1 = self.create_dial("", controlsEqRv_layout)
        self.empty_space1.hide()

        self.mid_slider = self.create_slider("Mid", controlsEqRv_layout)
        self.mid_slider.setValue(100)
        self.mid_slider.setRange(50, 150)

        self.empty_space2 = self.create_dial("", controlsEqRv_layout)
        self.empty_space2.hide()

        self.bass_slider = self.create_slider("Bass", controlsEqRv_layout)
        self.bass_slider.setValue(100)
        self.bass_slider.setRange(50, 150)

        self.empty_space3 = self.create_dial("", controlsEqRv_layout)
        self.empty_space3.hide()

        reverb_layout = QVBoxLayout()
        self.decay_dial = self.create_dial("Decay", reverb_layout, 1)
        self.decay_dial.setRange(0, 100)
        self.wetness_dial = self.create_dial("Wetness", reverb_layout)
        self.wetness_dial.setRange(0, 100)
        Dl_layout.addWidget(QLabel("Delay [ms]"))
        self.delay_input = QSpinBox()
        self.delay_input.setRange(0, 5000)
        self.delay_input.setValue(0)
        Dl_layout.addWidget(self.delay_input)
        reverb_layout.addLayout(Dl_layout)

        controlsEqRv_layout.addLayout(reverb_layout)
        controls_layout.addLayout(controlsEqRv_layout)

        threshold_layout = QHBoxLayout()
        self.threshold_input = QSpinBox()
        self.threshold_input.setRange(-50, 50)
        self.threshold_input.setValue(0)
        Th_layout.addWidget(QLabel("Threshold [dB]"))
        Th_layout.addWidget(self.threshold_input)
        threshold_layout.addLayout(Th_layout)
        self.level_dial = self.create_dial("Level", threshold_layout)
        controlsThGn_layout.addLayout(threshold_layout)

        self.gain_input = QSpinBox()
        self.gain_input.setRange(-50, 50)
        self.gain_input.setValue(0)
        Gn_layout.addWidget(QLabel("Gain [dB]"))
        Gn_layout.addWidget(self.gain_input)
        controlsThGn_layout.addLayout(Gn_layout)

        main_controls_layout.addLayout(controls_layout)
        main_controls_layout.addLayout(controlsThGn_layout)
        main_layout_bottom.addLayout(main_controls_layout)

        self.file_table = QTableWidget(2, 4)
        self.file_table.setHorizontalHeaderLabels(["File name", "File size [B]", "Time [s]", "Max Amplitude [dB]"])
        self.file_table.horizontalHeader().setStyleSheet("color: black")
        TbRf_layout.addWidget(self.file_table)
        self.refresh_button = QPushButton("Refresh", self)
        self.refresh_button.clicked.connect(self.refresh_action)
        TbRf_layout.addWidget(self.refresh_button)
        main_layout_bottom.addLayout(TbRf_layout)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        main_layout.addLayout(main_layout_bottom)

        self.setStyleSheet("""
            QWidget {
                background-color: #2e2e2e;
                color: #ffffff;
                font-family: Arial, sans-serif;
            }

            QPushButton {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 10px 20px;
                text-align: center;
                font-size: 16px;
                cursor: pointer;
                border-radius: 5px;
            }

            QPushButton:hover {
                background-color: #45a049;
            }

            QSlider, QDial, QSpinBox {
                background-color: #444444;
                color: white;
                border-radius: 5px;
                padding: 5px;
            }

            QSlider::handle:horizontal {
                background: #4CAF50;
                border-radius: 5px;
                width: 10px;
            }

            QDial {
                border: 2px solid #4CAF50;
            }

            QTableWidget {
                background-color: #333333;
                color: white;
            }

            QTableWidget::item {
                padding: 5px;
            }

            QTableWidget::horizontalHeader {
                background-color: #444444;
            }
        """)

    def at_action_graph(self):
        self.graphType = "A(t)"

    def af_action_graph(self):
        self.graphType = "A(f)"

    def create_slider(self, label_text, layout):
        slider_layout = QVBoxLayout()
        slider = QSlider(Qt.Vertical)
        slider.setRange(0, 100)
        slider.setValue(50)
        slider_layout.addWidget(QLabel(label_text))
        slider_layout.addWidget(slider)
        layout.addLayout(slider_layout)
        return slider

    def create_dial(self, label_text, layout, value=0):
        dial_layout = QVBoxLayout()
        dial = QDial()
        dial.setRange(0, 100)
        dial.setValue(value)
        dial_layout.addWidget(QLabel(label_text))
        dial_layout.addWidget(dial)
        layout.addLayout(dial_layout)
        return dial


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AudioGUI()
    window.show()
    sys.exit(app.exec_())
