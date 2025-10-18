# blink_detector.py
import math
import numpy as np
import mediapipe as mp
from collections import deque
import time

mp_face_mesh = mp.solutions.face_mesh

# landmark indices for eyes in mediapipe face mesh
LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]

def _euclid(a, b):
    return math.hypot(a[0]-b[0], a[1]-b[1])

def eye_aspect_ratio(landmarks, eye_indices, image_w, image_h):
    # returns EAR for one eye
    pts = []
    for idx in eye_indices:
        lm = landmarks[idx]
        pts.append((lm.x * image_w, lm.y * image_h))
    # p1 p2 p3 p4 p5 p6 corresponds to indexes used in EAR formula
    p1, p2, p3, p4, p5, p6 = pts
    vertical1 = _euclid(p2, p6)
    vertical2 = _euclid(p3, p5)
    horizontal = _euclid(p1, p4)
    if horizontal == 0:
        return 0.0
    ear = (vertical1 + vertical2) / (2.0 * horizontal)
    return ear

class BlinkDetector:
    def __init__(self, ear_threshold=0.24, consec_frames=3):
        self.ear_threshold = ear_threshold
        self.consec_frames = consec_frames
        self.counter = 0
        self.total_blinks = 0
        self.last_blink_time = None
        self.closed_start = None
        self.face_mesh = mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        # rolling queue of timestamps for last minute
        self.blink_times = deque()

    def process(self, image_rgb, image_w, image_h):
        results = self.face_mesh.process(image_rgb)
        ear = None
        alert = None

        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark
            left_ear = eye_aspect_ratio(landmarks, LEFT_EYE, image_w, image_h)
            right_ear = eye_aspect_ratio(landmarks, RIGHT_EYE, image_w, image_h)
            ear = (left_ear + right_ear) / 2.0

            if ear < self.ear_threshold:
                self.counter += 1
                if self.closed_start is None:
                    self.closed_start = time.time()
            else:
                if self.counter >= self.consec_frames:
                    self.total_blinks += 1
                    ts = time.time()
                    self.blink_times.append(ts)
                    # drop blinks older than 60 seconds
                    while self.blink_times and (ts - self.blink_times[0] > 60):
                        self.blink_times.popleft()
                self.counter = 0
                self.closed_start = None

            # drowsiness / eyes closed for long time
            if self.closed_start and (time.time() - self.closed_start) > 2.0:
                alert = "Eyes closed > 2s — possible drowsiness"
        return ear, self.total_blinks, len(self.blink_times), alert

    def close(self):
        self.face_mesh.close()
