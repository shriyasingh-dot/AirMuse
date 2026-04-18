import numpy as np

class GestureEngine:
    def __init__(self, fps=30):
        # Stability filter vars (must persist ~0.7 sec)
        self.threshold_frames = int(fps * 0.7) 
        self.gesture_history = {"Right": None, "Left": None}
        self.history_count = {"Right": 0, "Left": 0}
        
        # Motion paths for swipe detection
        self.path_history = {"Right": [], "Left": []}
        
    def _get_distance(self, p1, p2):
        return np.linalg.norm(np.array(p1) - np.array(p2))

    def detect_static(self, hand_data, frame_shape):
        label = hand_data['label']
        raw_lms = hand_data['landmarks']
        h, w, _ = frame_shape
        lms = [(int(lm.x * w), int(lm.y * h)) for lm in raw_lms]
        
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
            
        peace = fingers_extended[1] and fingers_extended[2] and not fingers_extended[3] and not fingers_extended[4]
        three = fingers_extended[1] and fingers_extended[2] and fingers_extended[3] and not fingers_extended[4]
        
        # 1 finger and 4 fingers logic (ignoring thumb for stability)
        one = fingers_extended[1] and not any(fingers_extended[2:])
        four = all(fingers_extended[1:])
        
        all_fingers_open = all(fingers_extended)
        all_fingers_closed = not any(fingers_extended)
        
        raw_gesture = "None"
        # Since 'four' doesn't check thumb, all_fingers_open will naturally trigger 'Open_Palm' before 'Four'
        if all_fingers_open:
            raw_gesture = "Open_Palm"
        elif all_fingers_closed:
            raw_gesture = "Fist"
        elif four:
            raw_gesture = "Four"
        elif three:
            raw_gesture = "Three"
        elif peace:
            raw_gesture = "Peace"
        elif one:
            raw_gesture = "One"
            
        # Swipe logic
        self.path_history[label].append(wrist)
        if len(self.path_history[label]) > 8:
            self.path_history[label].pop(0)
            
        if len(self.path_history[label]) == 8:
            dx = self.path_history[label][-1][0] - self.path_history[label][0][0]
            # Fast horizontal movement with minimal vertical
            if abs(dx) > 80 and abs(dx) > abs(self.path_history[label][-1][1] - self.path_history[label][0][1]):
                if dx > 0:
                    raw_gesture = "Swipe_Right"
                else:
                    raw_gesture = "Swipe_Left"
                self.path_history[label].clear()
            
        # Stability filter logic for static gestures (Swipe bypasses this)
        if raw_gesture in ["Swipe_Right", "Swipe_Left"]:
            return raw_gesture
            
        if raw_gesture == self.gesture_history[label]:
            self.history_count[label] += 1
        else:
            self.gesture_history[label] = raw_gesture
            self.history_count[label] = 1
            
        if self.history_count[label] >= self.threshold_frames:
            # Continuous triggers for hold-to-accelerate
            if raw_gesture in ["Peace", "Three", "One", "Four"]:
                return raw_gesture
            # Single discrete trigger for others
            elif self.history_count[label] == self.threshold_frames:
                return raw_gesture
        return "None"
