# main.py
import cv2
import time
import numpy as np
from blink_detector import BlinkDetector
from posture_detector import PostureDetector
from data_logger import DataLogger

# optional desktop notification
try:
    from plyer import notification
    HAVE_PLYER = True
except Exception:
    HAVE_PLYER = False

def notify(title, message):
    if HAVE_PLYER:
        notification.notify(title=title, message=message, timeout=3)

def draw_overlay(frame, ear, blinks_total, blinks_min, posture_angle, alerts):
    h, w = frame.shape[:2]
    # status text
    cv2.putText(frame, f"EAR: {ear:.3f}" if ear is not None else "EAR: --", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
    cv2.putText(frame, f"Total blinks: {blinks_total}", (10,60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)
    cv2.putText(frame, f"Blinks last 60s: {blinks_min}", (10,90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)
    cv2.putText(frame, f"Torso angle: {posture_angle:.1f}°" if posture_angle is not None else "Torso angle: --", (10,120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)
    # alerts
    y = 160
    for a in alerts:
        cv2.putText(frame, f"ALERT: {a}", (10,y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)
        y += 30
    return frame

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open webcam")
        return

    blink = BlinkDetector()
    posture = PostureDetector()
    logger = DataLogger()

    last_log = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            h, w = frame.shape[:2]
            # flip for selfie view
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            ear, total_blinks, blinks_min, blink_alert = blink.process(rgb, w, h)
            posture_angle, posture_alert = posture.process(rgb, w, h)

            alerts = []
            if blink_alert:
                alerts.append(blink_alert)
                notify("Blink Alert", blink_alert)
            if posture_alert:
                alerts.append(posture_alert)
                notify("Posture Alert", posture_alert)

            # log every 5 seconds
            if time.time() - last_log > 5:
                logger.log(ear, total_blinks, blinks_min, posture_angle, "; ".join(alerts) if alerts else "")
                last_log = time.time()

            out = draw_overlay(frame, ear if ear else 0.0, total_blinks, blinks_min, posture_angle if posture_angle else 0.0, alerts)
            cv2.imshow("Smart Health Monitor", out)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

    except KeyboardInterrupt:
        pass
    finally:
        cap.release()
        cv2.destroyAllWindows()
        blink.close()
        posture.close()
        print("Exiting...")

if __name__ == "__main__":
    main()
