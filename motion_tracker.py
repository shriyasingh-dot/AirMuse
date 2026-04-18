import numpy as np

class MotionTracker:
    def __init__(self):
        self.alpha = 0.2
        self.smoothed_volume = 0.5
        
        # DSP Accumulator parameters
        self.prev_x = None
        self.prev_y = None
        self.speed = 1.0
        self.bass_level = 0.0
        self.reverb_level = 0.0
        self.history = []
        
    def _get_distance(self, p1, p2):
        return np.linalg.norm(np.array(p1) - np.array(p2))

    def compute_pinch(self, hand_data, frame_shape):
        raw_lms = hand_data['landmarks']
        h, w, _ = frame_shape
        lms = [(int(lm.x * w), int(lm.y * h)) for lm in raw_lms]
        
        distance = self._get_distance(lms[4], lms[8]) # thumb and index
        
        max_dist = 150.0
        min_dist = 20.0
        
        v_target = np.clip((distance - min_dist) / (max_dist - min_dist), 0.0, 1.0)
        
        # Heavy analog smoothing (80% historical, 20% target)
        self.smoothed_volume = 0.8 * self.smoothed_volume + 0.2 * v_target
        return self.smoothed_volume

    def compute_effects(self, hand_data, frame_shape):
        raw_lms = hand_data['landmarks']
        h, w, _ = frame_shape
        lms = [(int(lm.x * w), int(lm.y * h)) for lm in raw_lms]
        
        palm_x, palm_y = lms[9]
        
        if self.prev_x is None or self.prev_y is None:
            self.prev_x = palm_x
            self.prev_y = palm_y
            return self.speed, self.bass_level, self.reverb_level

        dx = palm_x - self.prev_x
        dy = palm_y - self.prev_y

        # Deadzone logic
        if abs(dy) < 5:
            dy = 0

        # Accumulate Vertical Motion (Speed/Tempo)
        if abs(dy) > 8:
            self.speed += (-dy) * 0.0004
            
        self.speed = max(0.5, min(2.0, self.speed))
        
        # Redundant stabilization
        self.speed = 0.9 * self.speed + 0.1 * self.speed

        self.prev_x = palm_x
        self.prev_y = palm_y
        
        return self.speed, self.bass_level, self.reverb_level
