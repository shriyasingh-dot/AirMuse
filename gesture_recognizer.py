import cv2
import numpy as np
import collections
import urllib.request
import os
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

class GestureRecognizer:
    def __init__(self):
        self.model_path = 'hand_landmarker.task'
        if not os.path.exists(self.model_path):
            print("Downloading hand_landmarker.task...")
            url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
            urllib.request.urlretrieve(url, self.model_path)
            
        base_options = python.BaseOptions(model_asset_path=self.model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=2,
            running_mode=vision.RunningMode.VIDEO)
        self.detector = vision.HandLandmarker.create_from_options(options)
        
        # History for dynamic gestures
        self.right_wrist_history = collections.deque(maxlen=20)
        self.left_history = collections.deque(maxlen=30)
        self.swipe_cooldown = 0
        self.discrete_cooldown = 0
        self.frame_timestamp_ms = 0
        
        # Connections for drawing
        self.connections = [(0, 1), (1, 2), (2, 3), (3, 4), 
                            (0, 5), (5, 6), (6, 7), (7, 8), 
                            (5, 9), (9, 10), (10, 11), (11, 12), 
                            (9, 13), (13, 14), (14, 15), (15, 16), 
                            (13, 17), (0, 17), (17, 18), (18, 19), (19, 20)]
        
    def _get_distance(self, p1, p2):
        return np.linalg.norm(np.array(p1) - np.array(p2))

    def process_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        import time
        self.frame_timestamp_ms = int(time.time() * 1000)
        
        result = self.detector.detect_for_video(mp_image, self.frame_timestamp_ms)
        
        commands = {
            'right_discrete': None,
            'left_continuous': {
                'volume': None,
                'speed': None,
                'reverb': None,
                'filter': None
            }
        }
        
        if self.swipe_cooldown > 0:
            self.swipe_cooldown -= 1
        if self.discrete_cooldown > 0:
            self.discrete_cooldown -= 1
            
        if not result.hand_landmarks:
            return frame, commands
            
        h, w, c = frame.shape
        
        for hand_idx, hand_landmarks in enumerate(result.hand_landmarks):
            handedness = result.handedness[hand_idx][0].category_name
            # Typically Left and Right are mirrored, we must check which one
            label = handedness
            
            lms = []
            for lm in hand_landmarks:
                lx, ly = int(lm.x * w), int(lm.y * h)
                lms.append((lx, ly))
                cv2.circle(frame, (lx, ly), 5, (0, 255, 0), -1)
                
            for fr, to in self.connections:
                if fr < len(lms) and to < len(lms):
                    cv2.line(frame, lms[fr], lms[to], (255, 0, 0), 2)
            
            fingers_extended = [False]*5
            tips = [4, 8, 12, 16, 20]
            pips = [2, 6, 10, 14, 18]
            wrist = lms[0]
            
            for i in range(1, 5): 
                if self._get_distance(lms[tips[i]], wrist) > self._get_distance(lms[pips[i]], wrist):
                    fingers_extended[i] = True
            
            if label == "Right":
                fingers_extended[0] = lms[4][0] < lms[5][0]
            else:
                fingers_extended[0] = lms[4][0] > lms[5][0]
                
            open_palm = all(fingers_extended)
            fist = not any(fingers_extended)
            peace = fingers_extended[1] and fingers_extended[2] and not fingers_extended[3] and not fingers_extended[4]
            rock = fingers_extended[1] and not fingers_extended[2] and not fingers_extended[3] and fingers_extended[4]
            
            if label == "Right":
                if self.discrete_cooldown == 0:
                    if rock:
                        commands['right_discrete'] = "Remix"
                        self.discrete_cooldown = 40
                    elif peace:
                        commands['right_discrete'] = "Loop"
                        self.discrete_cooldown = 40
                    elif open_palm:
                        commands['right_discrete'] = "Play_Pause"
                        self.discrete_cooldown = 40
                    elif fist:
                        commands['right_discrete'] = "Stop"
                        self.discrete_cooldown = 40
                        
                self.right_wrist_history.append(lms[0][0])
                if self.swipe_cooldown == 0 and len(self.right_wrist_history) == 20:
                    start_x = self.right_wrist_history[0]
                    end_x = self.right_wrist_history[-1]
                    if end_x - start_x > 200:
                        commands['right_discrete'] = "Swipe_Right"
                        self.swipe_cooldown = 40
                        self.right_wrist_history.clear()
                    elif start_x - end_x > 200:
                        commands['right_discrete'] = "Swipe_Left"
                        self.swipe_cooldown = 40
                        self.right_wrist_history.clear()

            elif label == "Left":
                pinch_dist = self._get_distance(lms[4], lms[8])
                vol = np.clip((pinch_dist - 20) / 150, 0.0, 1.0)
                commands['left_continuous']['volume'] = vol
                
                palm_y = lms[9][1]
                speed = np.clip(1.0 + (h/2 - palm_y) / (h/3), 0.5, 2.0)
                commands['left_continuous']['speed'] = speed
                
                palm_x = lms[9][0]
                filter_val = np.clip(palm_x / w, 0.0, 1.0)
                commands['left_continuous']['filter'] = filter_val
                
                span = self._get_distance(lms[4], lms[20])
                reverb = np.clip((span - 100) / 150, 0.0, 0.8)
                commands['left_continuous']['reverb'] = reverb

        return frame, commands
