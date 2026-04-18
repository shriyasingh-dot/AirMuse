import cv2
import time
import os
import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QFileDialog
from frontend.ui import GestureUI
from backend.hand_tracker import HandTracker
from backend.gesture_engine import GestureEngine
from backend.motion_tracker import MotionTracker
from backend.audio_engine import AudioEngine

def main():
    app = QApplication(sys.argv)
    
    print("Please select an audio file (mp3/wav) for AirMuse...")
    file_path, _ = QFileDialog.getOpenFileName(
        None, "Select Audio File", "", "Audio Files (*.mp3 *.wav);;All Files (*.*)"
    )
    if not file_path:
        print("No file selected. Exiting.")
        return

    window = GestureUI()
    window.show()

    # Initialize modules
    audio = AudioEngine()
    if not audio.load_track(file_path):
        return
        
    hand_tracker = HandTracker()
    gesture_engine = GestureEngine(fps=30)
    motion_tracker = MotionTracker()
    
    cap = cv2.VideoCapture(0)
    print("Starting Main Loop... Press 'q' to quit in the OpenCV window.")
    
    # FPS Tracking
    prev_time = 0
    
    # Cooldown system per PRD
    cooldown_frames = 0
    cooldown_max = 30 # roughly 1 second
    last_gesture = "None"

    # We will assume: Right hand = Gestures, Left hand = Volume
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
            
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        
        curr_time = time.time()
        fps = int(1 / (curr_time - prev_time)) if prev_time > 0 else 30
        prev_time = curr_time
        
        timestamp_ms = int(curr_time * 1000)
        
        # 1. Process hands
        hands_data = hand_tracker.process(frame, timestamp_ms)
        
        if cooldown_frames > 0:
            cooldown_frames -= 1
            
        current_gesture = "None"
        
        # Draw and extract logic
        for hand in hands_data:
            label = hand['label']
            lms = hand['landmarks']
            
            # Simple minimal rendering
            for lm in lms:
                lx, ly = int(lm.x * w), int(lm.y * h)
                cv2.circle(frame, (lx, ly), 5, (0, 255, 0), -1)

            if label == "Right":
                # Continuous INTENSITY tracking (Pinch volume)
                vol = motion_tracker.compute_pinch(hand, frame.shape)
                audio.set_volume(vol)
                
                # Discrete COMMAND tracking
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
                # Discrete Sign-based Tempo tracking
                gesture = gesture_engine.detect_static(hand, frame.shape)
                if gesture != "None":
                    current_gesture = gesture
                
                # "Hold to accelerate" UX for Tempo
                if gesture == "Peace":
                    motion_tracker.speed += 0.01
                elif gesture == "Three":
                    motion_tracker.speed -= 0.01
                    
                motion_tracker.speed = max(0.5, min(2.0, motion_tracker.speed))
                
                # "Hold to accelerate" UX for Bass
                if gesture == "One":
                    motion_tracker.bass_level += 0.2
                elif gesture == "Four":
                    motion_tracker.bass_level -= 0.2
                    
                motion_tracker.bass_level = max(-5.0, min(5.0, motion_tracker.bass_level))
                
                # Clean DSP handoff
                audio.set_dsp_effects(motion_tracker.speed, motion_tracker.bass_level, 0.0)
                
        # 5. Native QT UI Update
        window.update_ui(audio.volume, motion_tracker.speed, motion_tracker.bass_level, audio.is_playing)
        app.processEvents()

        cv2.imshow("AirMuse - Camera Feed", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    audio.stop_audio()

if __name__ == "__main__":
    main()
