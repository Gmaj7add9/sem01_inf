import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QVBoxLayout, QHBoxLayout, QSlider, QDial, QPushButton, \
    QLineEdit, QLabel, QSpinBox, QWidget, QFileDialog, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QColor, QBrush
from pyqtgraph import PlotWidget
import wave
import numpy as np
from pydub import AudioSegment


class ThresholdSlider(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(35)
        self.setFixedHeight(200)
        self.value = 50
        self.setMouseTracking(True)
        self.handle_position = self.height() - (self.value / 100) * self.height()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        background_color = QColor(251, 233, 208)
        painter.setBrush(QBrush(background_color))
        painter.drawRect(0, 0, self.width(), self.height())

        slider_color = QColor(144, 174, 173)
        painter.setBrush(QBrush(slider_color))

        slider_height = int(self.height() * (self.value / 100))
        painter.drawRect(0, self.height() - slider_height, self.width(), slider_height)

        handle_width = 120
        handle_height = 20
        handle_position_int = int(self.handle_position)

        handle_rect = QRect(self.width() // 2 - handle_width // 2, handle_position_int - handle_height // 2,
                            handle_width, handle_height)
        painter.setBrush(QBrush(QColor(135, 79, 65)))
        painter.drawRect(handle_rect)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.update_value(event.pos())

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.update_value(event.pos())

    def update_value(self, pos):
        new_value = int(100 * (self.height() - pos.y()) / self.height())
        new_value = max(5, min(95, new_value))

        if new_value != self.value:
            self.value = new_value
            self.handle_position = self.height() - (self.value / 100) * self.height()
            self.update()


class AudioGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audio GUI")
        self.setGeometry(100, 100, 1000, 600)

        self.setStyleSheet("""
            background-color: #FBE9D0;
            font-family: 'Courier New', Courier, monospace;
            font-weight: bold;
            font-size: 12px;
        """)

        main_widget = QWidget()
        main_layout = QVBoxLayout()

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
        graph_menu.addAction(at_action)
        graph_menu.addAction(af_action)

        menu_bar.setStyleSheet("""
            QMenuBar {
                background-color: #E64833;
                color: white;
                font-size: 14px;
                font-family: 'Courier New', Courier, monospace;
                font-weight: bold;
            }
            QMenuBar::item:selected {
                background-color: #FBE9D0;
                color: #E64833;
            }
        """)

        top_bar_layout = QHBoxLayout()

        self.file_table = QTableWidget(2, 4)
        self.file_table.setHorizontalHeaderLabels(["File name", "File size [B]", "Time [s]", "Max Amplitude [dB]"])

        header = self.file_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.file_table.setStyleSheet("""
            background-color: #FBE9D0;
            font-size: 12px;
        """)
        top_bar_layout.addWidget(self.file_table, 2)

        top_bar_layout.addStretch()
        refresh_button = QPushButton("REFRESH")
        refresh_button.setStyleSheet(
            "background-color: #E64833; color: white; font-size: 14px; font-weight: bold; padding: 10px 20px; border: none; border-radius: 10px;"
        )
        refresh_button.clicked.connect(self.refresh_action)
        refresh_button.setFixedSize(150, 50)
        top_bar_layout.addWidget(refresh_button)

        main_layout.addLayout(top_bar_layout)

        self.graph = PlotWidget()
        main_layout.addWidget(self.graph)
        self.graph.setFixedSize(1000, 400)

        controls_layout = QHBoxLayout()

        sliders_layout = QHBoxLayout()
        sliders_layout.setSpacing(50)

        self.treble_slider = self.create_threshold_slider_with_label("Treble", sliders_layout)
        self.mid_slider = self.create_threshold_slider_with_label("Mid", sliders_layout)
        self.bass_slider = self.create_threshold_slider_with_label("Bass", sliders_layout)

        sliders_container = QWidget()
        sliders_container.setLayout(sliders_layout)
        sliders_container.setStyleSheet("background-color: #E64833; border-radius: 10px; padding: 10px;")
        controls_layout.addWidget(sliders_container)

        decay_wetness_layout = QVBoxLayout()

        decay_container = self.create_dial_container("Decay")
        decay_wetness_layout.addWidget(decay_container)

        wetness_container = self.create_dial_container("Wetness")
        decay_wetness_layout.addWidget(wetness_container)

        controls_layout.addLayout(decay_wetness_layout)

        self.gain_dial = self.create_dial("Gain [dB]", controls_layout, value=100)
        self.level_dial = self.create_dial("Level", controls_layout)

        threshold_container = QWidget()
        threshold_container.setStyleSheet("background-color: #E64833; border-radius: 10px; padding: 10px;")
        threshold_container.setFixedWidth(95)

        threshold_layout = QVBoxLayout()
        threshold_label = QLabel("Threshold")
        threshold_label.setAlignment(Qt.AlignCenter)
        threshold_label.setStyleSheet("font-size: 12px;")

        self.threshold_slider = ThresholdSlider()

        threshold_layout.addWidget(threshold_label)
        threshold_layout.addWidget(self.threshold_slider)

        threshold_container.setLayout(threshold_layout)
        threshold_layout.setAlignment(Qt.AlignCenter)

        controls_layout.addWidget(threshold_container)

        main_layout.addLayout(controls_layout)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def create_threshold_slider_with_label(self, label_text, layout):
        slider_layout = QVBoxLayout()

        label = QLabel(label_text)
        label.setStyleSheet("padding: 2px; font-size: 12px;")
        label.setAlignment(Qt.AlignCenter)

        slider = ThresholdSlider()
        slider_layout.addWidget(label)
        slider_layout.addWidget(slider)

        layout.addLayout(slider_layout)
        return slider

    def setup_sliders(self):
        self.treble_slider.setStyleSheet("background-color: #E64833; border-radius: 10px;")
        self.mid_slider.setStyleSheet("background-color: #E64833; border-radius: 10px;")
        self.bass_slider.setStyleSheet("background-color: #E64833; border-radius: 10px;")

    def create_dial(self, label_text, layout, value=0):
        dial_layout = QVBoxLayout()
        dial_container = QWidget()
        dial_container.setStyleSheet("background-color: #E64833; border-radius: 10px; padding: 10px;")
        dial_inner_layout = QVBoxLayout()
        dial = QDial()
        dial.setRange(0, 100)
        dial.setValue(value)
        dial_inner_layout.addWidget(QLabel(label_text))
        dial_inner_layout.addWidget(dial)
        dial_container.setLayout(dial_inner_layout)
        dial_layout.addWidget(dial_container)
        layout.addLayout(dial_layout)
        return dial

    def create_dial_container(self, label_text):
        dial_container = QWidget()
        dial_container.setStyleSheet("""
            background-color: #E64833; 
            border-radius: 10px; 
            padding: 20px; 
            margin-bottom: 0px;
        """)
        dial_container.setFixedSize(150, 180)

        dial_inner_layout = QVBoxLayout()
        dial_inner_layout.addWidget(QLabel(label_text))
        dial = QDial()
        dial.setRange(0, 100)
        dial.setValue(50)
        dial_inner_layout.addWidget(dial)
        dial_container.setLayout(dial_inner_layout)
        return dial_container

    def table_update(self, file_path):
        import os
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)

        with wave.open(file_path, 'rb') as wav_file:
            n_frames = wav_file.getnframes()
            framerate = wav_file.getframerate()
            duration = n_frames / framerate

        # Add or update the first row in the table
        self.file_table.setItem(0, 0, QTableWidgetItem(file_name))
        self.file_table.setItem(0, 1, QTableWidgetItem(str(file_size)))
        self.file_table.setItem(0, 2, QTableWidgetItem(f"{duration:.2f}"))

        # You might want to calculate max amplitude here if needed
        self.file_table.setItem(0, 3, QTableWidgetItem("N/A"))

    def load_wave(self, file_path):
        with wave.open(file_path, 'rb') as wav_file:
            # Store wave file parameters
            self.wav_params = wav_file.getparams()
            n_channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            framerate = wav_file.getframerate()
            n_frames = wav_file.getnframes()

            # Read entire file data
            data = wav_file.readframes(n_frames)

            # Convert to numpy array
            wave_data = np.frombuffer(data, dtype=np.int16)

            # If stereo, average the channels to create mono
            if n_channels == 2:
                wave_data = wave_data.reshape(-1, 2).mean(axis=1)

            duration = n_frames / framerate
            time = np.linspace(0, duration, num=len(wave_data))

            self.graph.clear()
            self.graph.plot(time, wave_data, pen='r')

            # Store raw data for potential saving
            self.raw_audio_data = wave_data
            self.audio_file_path = file_path

    def open_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open WAV File", "", "WAV Files (*.wav)", options=options)
        if file_path:
            self.load_wave(file_path)
            self.table_update(file_path)

    def refresh_action(self):
        print("Refresh button clicked!")

    def values_ r(self):
        EQ_List = [self.bass_slider.value, self.mid_slider.value, self.treble_slider.value]
        Echo_List = []  # Need to define the appropriate dials/inputs
        Distortion_List = []  # Need to define the appropriate dials/inputs
        return (EQ_List, Echo_List, Distortion_List)

    def save_audio(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Audio", "", "WAV (*.wav)")

        if file_path and hasattr(self, 'raw_audio_data') and hasattr(self, 'wav_params'):
            try:
                with wave.open(file_path, 'wb') as out_file:
                    # Set to mono
                    out_file.setnchannels(1)
                    out_file.setsampwidth(2)  # 16-bit
                    out_file.setframerate(self.wav_params.framerate)
                    out_file.writeframes(self.raw_audio_data.astype(np.int16).tobytes())
                print(f"Audio saved successfully to: {file_path}")
            except Exception as e:
                print(f"Save error: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AudioGUI()
    window.show()
    sys.exit(app.exec_())