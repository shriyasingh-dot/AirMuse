<div align="center">
  
# 🎧 AirMuse  
**Touchless Music Control & Real-Time AirMuse Interface**

[![Python Version](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-Tracking-orange.svg)](https://developers.google.com/mediapipe)
[![PyQt5](https://img.shields.io/badge/PyQt5-UI-green.svg)](https://riverbankcomputing.com/software/pyqt/)

AirMuse is a real-time gesture-controlled music interface that allows users to manipulate audio playback and sound effects entirely through hand gestures via a standard webcam.
</div>

---

## 🎯 Core Functionality

The system detects hand gestures using advanced computer vision and maps them instantly to precise music controls.

### 🤚 Right Hand (Playback & Volume)
| Gesture | Action |
| --- | --- |
| **Open Palm** | Play / Pause |
| **Pinch** | Volume Control (smooth analog adjustment) |
| **Fist** | Stop |

### 🤚 Left Hand (Effects & Tempo)
| Gesture | Action |
| --- | --- |
| **2 Fingers** | Increase Tempo |
| **3 Fingers** | Decrease Tempo |
| **1 Finger** | Increase Bass |
| **4 Fingers** | Decrease Bass |

---

## 🎛️ Key Features

- **Real-Time Gesture Recognition:** Processed instantly with high frame-rate responsiveness.
- **Touchless Music Control:** Step away from the keyboard and control your music naturally.
- **Dynamic Audio Manipulation:** Precise, continuous manipulation of Volume, Tempo, and Bass.
- **Premium UI:** A sleek, dark-themed PyQt5 desktop interface featuring soft pink accents and real-time sliders.
- **Low-Latency Audio Response:** Custom audio processing ensures lag-free effects application.
- **Modular Architecture:** Clean separation of concerns between computer vision (gestures), audio processing (DSP), and presentation (UI).

---

## 🧠 Technical Highlights

- **Precise Core Tracking:** Leverages MediaPipe’s 21 hand landmarks for highly accurate gesture and pinch-distance detection.
- **Signal Processing:** Implements heavy signal smoothing, bounding, and deadzones to eliminate jitter, drift, and false triggers.
- **Custom Audio Engine:** Employs advanced signal processing to adjust DSP parameters on the fly.
- **Threaded Execution:** Separates backend vision processing from frontend UI rendering and non-blocking audio streams to maintain high performance.

---

## 🖥️ UI Design

AirMuse comes with a highly polished GUI tailored for live performance and effortless control.

- **Framework:** Custom PyQt5 desktop application.
- **Aesthetic:** Modern, minimalist dark theme highlighted with vibrant, soft pink accents and glassmorphism styling.
- **Live Visual Feedback:** Responsive, real-time sliders and visualizers for Volume, Tempo, and Bass.
- **Status Indicators:** Bold, clean indicators showing playback state (PLAYING / PAUSED).

---

## ⚙️ Installation

Follow these steps to set up AirMuse on your local machine:

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/AirMuse.git
   cd AirMuse
   ```

2. **Install dependencies**
   It is recommended to use a virtual environment.
   ```bash
   pip install -r requirements.txt
   ```
   *(Ensure you have OpenCV, MediaPipe, PyQt5, Sounddevice, and Numpy installed)*

3. **Add an audio file**
   Place your preferred `.wav` or `.mp3` track in the `assets/` folder (or configure the path in the app).

4. **Run the application**
   ```bash
   python main.py
   ```

---

## ▶️ Usage

1. **Launch the App:** Run `main.py` to start the GUI and initialize the webcam.
2. **Setup:** Ensure your webcam has a clear view of both of your hands.
3. **Control:**
   - Raise your **Right Hand** to start playback (Open Palm) or adjust volume (Pinch).
   - Use your **Left Hand** to manipulate the equalizer and tempo interactively.
   - Watch the UI sliders smoothly react to your movements.

---

## 📁 Project Structure

```text
AirMuse/
│── backend/               # Core processing modules
│   │── audio_engine.py    # DSP, sounddevice stream, and audio manipulation
│   │── gesture_engine.py  # OpenCV + MediaPipe gesture classification
│   │── hand_tracker.py    # Vision hand landmark extraction
│   └── motion_tracker.py  # Continuous control processing (vol, speed)
│── frontend/              # UI presentation layer
│   │── ui.py              # PyQt5 Frontend & styled components
│   └── templates/         # Web/Flask templates 
│── main.py                # Native Desktop Application Entry Point
│── app.py                 # Web/Flask Application Entry Point
│── assets/                # Audio files and UI design assets
│── requirements.txt       # Project dependencies
└── README.md              # You are here!
```

---

## 🚀 Future Improvements

- [ ] **Multi-track Mixing:** Support for stems and multiple tracks simultaneously.
- [ ] **Gesture Customization:** User-configurable mappings for different hand gestures.
- [ ] **Enhanced Audio Effects:** Integration of advanced VST-like effects (Reverb, High/Low Pass Filters, Delay).
- [ ] **Fluid UI Animations:** Upgraded micro-animations and transition effects in PyQt.
- [ ] **Cross-Platform Support:** Distributed binaries for seamless installation on Windows, macOS, and Linux.

---

<div align="center">
  <i>Designed and engineered for seamless musical interaction.</i>
</div>
