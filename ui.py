from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt5.QtCore import Qt
import sys

class GestureUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AirMuse 🎧")
        self.setGeometry(200, 200, 400, 320)

        # Layout
        layout = QVBoxLayout()

        # Title
        self.title = QLabel("AirMuse 🎧")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("""
            font-size: 26px;
            color: #ff4fa3;
            font-weight: bold;
        """)
        layout.addWidget(self.title)

        # Status
        self.status = QLabel("PAUSED")
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setStyleSheet("font-size: 16px; color: white;")
        layout.addWidget(self.status)

        # Sliders (progress bars)
        self.volume = QProgressBar()
        self.volume.setTextVisible(False)
        self.tempo = QProgressBar()
        self.tempo.setTextVisible(False)
        self.bass = QProgressBar()
        self.bass.setTextVisible(False)

        layout.addWidget(QLabel("Volume"))
        layout.addWidget(self.volume)

        layout.addWidget(QLabel("Tempo"))
        layout.addWidget(self.tempo)

        layout.addWidget(QLabel("Bass"))
        layout.addWidget(self.bass)

        self.setLayout(layout)

        # 💖 PINK THEME
        self.setStyleSheet("""
            QWidget {
                background-color: #0f0f14;
                color: #f8c8dc;
                font-family: Arial;
            }

            QLabel {
                font-size: 14px;
            }

            QProgressBar {
                border-radius: 8px;
                background: #2a2a35;
                height: 12px;
                border: none;
            }

            QProgressBar::chunk {
                background-color: #ff4fa3;
                border-radius: 8px;
            }
        """)

    def update_ui(self, vol, tempo, bass, playing):
        # vol: 0.0 -> 1.0 => 0 -> 100
        self.volume.setValue(int(vol * 100))
        # tempo: 0.5 -> 2.0. Map to 0 -> 100%. Range is 1.5.
        tempo_pct = max(0, min(100, int(((tempo - 0.5) / 1.5) * 100)))
        self.tempo.setValue(tempo_pct)
        # bass is currently passed as "bass_smoothed". If it's -5 to 5, we shift +5 (0 to 10), map to 100.
        bass_pct = max(0, min(100, int(((bass + 5.0) / 10.0) * 100)))
        self.bass.setValue(bass_pct)

        self.status.setText("PLAYING" if playing else "PAUSED")
