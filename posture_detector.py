# posture_detector.py
import mediapipe as mp
import math

mp_pose = mp.solutions.pose

def _midpoint(a, b):
    return ((a.x + b.x) / 2.0, (a.y + b.y) / 2.0)

def angle_between(v1, v2):
    # v1, v2 are tuples
    dot = v1[0]*v2[0] + v1[1]*v2[1]
    mag1 = math.hypot(v1[0], v1[1])
    mag2 = math.hypot(v2[0], v2[1])
    if mag1*mag2 == 0:
        return 0.0
    cosang = max(-1.0, min(1.0, dot/(mag1*mag2)))
    return math.degrees(math.acos(cosang))

class PostureDetector:
    def __init__(self, slouch_threshold_deg=15):
        self.pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.slouch_threshold_deg = slouch_threshold_deg

    def process(self, image_rgb, image_w, image_h):
        results = self.pose.process(image_rgb)
        alert = None
        posture_angle = None
        if results.pose_landmarks:
            lm = results.pose_landmarks.landmark
            # mediapipe pose indices
            left_sh = lm[11]; right_sh = lm[12]
            left_hip = lm[23]; right_hip = lm[24]
            # compute midpoints (normalized)
            mid_sh = _midpoint(left_sh, right_sh)
            mid_hip = _midpoint(left_hip, right_hip)

            # torso vector from hips to shoulders (normalized coordinates)
            torso_vec = (mid_sh[0] - mid_hip[0], mid_sh[1] - mid_hip[1])
            # vertical vector (0, -1) since y increases downward in image coords
            vertical_vec = (0.0, -1.0)
            posture_angle = angle_between(torso_vec, vertical_vec)
            # if torso tilts forward/back beyond threshold -> slouch
            if posture_angle > self.slouch_threshold_deg:
                alert = f"Bad posture: tilt {posture_angle:.1f}°"
        return posture_angle, alert

    def close(self):
        self.pose.close()
