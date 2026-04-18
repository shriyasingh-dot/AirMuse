import cv2
import time
import os
import threading
import tkinter as tk
from tkinter import filedialog
from flask import Flask, render_template, Response, jsonify

from backend.hand_tracker import HandTracker
from backend.gesture_engine import GestureEngine
from backend.motion_tracker import MotionTracker
from backend.audio_engine import AudioEngine

app = Flask(__name__, template_folder="frontend/templates")

# Global state
latest_frame = None
dj_state = {
    "status": "PAUSED",
    "gesture": "None",
    "volume": 0.5,
    "tempo": 1.0,
    "bass": 5.0,
    "track": "None"
}
lock = threading.Lock()

def process_tracking(file_path):
    global latest_frame, dj_state
    
    audio = AudioEngine()
    if not audio.load_track(file_path):
        print("Failed to load track")
        return
        
    hand_tracker = HandTracker()
    gesture_engine = GestureEngine(fps=30)
    motion_tracker = MotionTracker()
    
    cap = cv2.VideoCapture(0)
    
    prev_time = 0
    cooldown_frames = 0
    cooldown_max = 30
    last_gesture = "None"

    with lock:
        dj_state["track"] = os.path.basename(file_path)

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            time.sleep(0.01)
            continue
            
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        
        curr_time = time.time()
        timestamp_ms = int(curr_time * 1000)
        
        hands_data = hand_tracker.process(frame, timestamp_ms)
        
        if cooldown_frames > 0:
            cooldown_frames -= 1
            
        current_gesture = "None"
        
        for hand in hands_data:
            label = hand['label']
            lms = hand['landmarks']
            
            # Simple minimal rendering (keep landmarks)
            for lm in lms:
                lx, ly = int(lm.x * w), int(lm.y * h)
                cv2.circle(frame, (lx, ly), 5, (0, 255, 0), -1)

            if label == "Right":
                vol = motion_tracker.compute_pinch(hand, frame.shape)
                audio.set_volume(vol)
                
                gesture = gesture_engine.detect_static(hand, frame.shape)
                if gesture != "None":
                    current_gesture = gesture
                    last_gesture = gesture
                    if cooldown_frames == 0:
                        if gesture == "Open_Palm":
                            audio.trigger_play_pause()
                            cooldown_frames = cooldown_max
                        elif gesture == "Fist":
                            audio.stop_audio()
                            cooldown_frames = cooldown_max
                        elif gesture == "Swipe_Right":
                            audio.jump_time(10)
                            cooldown_frames = cooldown_max
                        elif gesture == "Swipe_Left":
                            audio.jump_time(-10)
                            cooldown_frames = cooldown_max
                        
            elif label == "Left":
                gesture = gesture_engine.detect_static(hand, frame.shape)
                if gesture != "None":
                    current_gesture = gesture
                
                if gesture == "Peace":
                    motion_tracker.speed += 0.01
                elif gesture == "Three":
                    motion_tracker.speed -= 0.01
                    
                motion_tracker.speed = max(0.5, min(2.0, motion_tracker.speed))
                
                if gesture == "One":
                    motion_tracker.bass_level += 0.2
                elif gesture == "Four":
                    motion_tracker.bass_level -= 0.2
                    
                motion_tracker.bass_level = max(-5.0, min(5.0, motion_tracker.bass_level))
                
                audio.set_dsp_effects(motion_tracker.speed, motion_tracker.bass_level, 0.0)
        
        # Draw floating glow dot only (no text)
        if current_gesture != "None":
            # Glow effect dot in center or fixed spot
            # Top right for Web so it doesn't overlap left dashboard
            cv2.circle(frame, (w - 40, 40), 15, (180, 105, 255), -1)
            
        with lock:
            dj_state["status"] = "PLAYING" if audio.is_playing else "PAUSED"
            dj_state["gesture"] = last_gesture
            dj_state["volume"] = audio.volume
            dj_state["tempo"] = motion_tracker.speed
            dj_state["bass"] = motion_tracker.bass_level + 5.0  # normalize 0 to 10
            
            # encode frame
            ret, buffer = cv2.imencode('.jpg', frame)
            if ret:
                latest_frame = buffer.tobytes()

    cap.release()
    audio.stop_audio()

def generate_frames():
    global latest_frame
    while True:
        with lock:
            if latest_frame is None:
                frame = None
            else:
                frame = latest_frame
        
        if frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            time.sleep(0.05)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/state')
def get_state():
    with lock:
        return jsonify(dj_state)

if __name__ == "__main__":
    # Standard setup
    root = tk.Tk()
    root.withdraw()
    
    print("Please select an audio file (mp3/wav) for AirMuse...")
    file_path = filedialog.askopenfilename(
        title="Select Audio File",
        filetypes=[("Audio Files", "*.mp3 *.wav"), ("All Files", "*.*")]
    )
    if not file_path:
        print("No file selected. Exiting.")
        exit(0)
        
    # Start tracking background thread
    tracking_thread = threading.Thread(target=process_tracking, args=(file_path,), daemon=True)
    tracking_thread.start()
    
    # Run flask
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
