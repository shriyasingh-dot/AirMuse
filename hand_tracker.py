import cv2
import urllib.request
import os
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

class HandTracker:
    def __init__(self):
        self.model_path = os.path.join(os.path.dirname(__file__), 'hand_landmarker.task')
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
        
    def process(self, frame, timestamp_ms):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        result = self.detector.detect_for_video(mp_image, timestamp_ms)
        
        hands_data = []
        if result.hand_landmarks:
            for hand_idx, landmarks in enumerate(result.hand_landmarks):
                # MedianPipe returns mirrored results. Since we flipped the frame, 
                # "Left" means physical "Right" hand.
                handedness = result.handedness[hand_idx][0].category_name
                corrected_label = "Right" if handedness == "Left" else "Left"
                hands_data.append({
                    "label": corrected_label,
                    "landmarks": landmarks
                })
        return hands_data
