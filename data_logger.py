# data_logger.py
import os
import csv
import time
from datetime import datetime
from firebase_logger import init_firebase, push_log

LOG_DIR = "logs"
CSV_PATH = os.path.join(LOG_DIR, "health_log.csv")

class DataLogger:
    def __init__(self, csv_path=CSV_PATH):
        os.makedirs(LOG_DIR, exist_ok=True)
        self.csv_path = csv_path
        # create file with header if not exists
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "ear", "total_blinks", "blinks_last_min", "posture_angle", "alert"])
        
        self.firebase_ref = None
        try:
            # change the URL below to match your Firebase project URL
            self.firebase_ref = init_firebase(
                db_url="https://smarthealthmonitor-default-rtdb.asia-southeast1.firebasedatabase.app/"
            )
            print("✅ Connected to Firebase successfully")
        except Exception as e:
            print("⚠️ Firebase init failed:", e)


    def log(self, ear, total_blinks, blinks_last_min, posture_angle, alert):
        ts = datetime.now().isoformat()
        with open(self.csv_path, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([ts, ear if ear is not None else "", total_blinks, blinks_last_min, posture_angle if posture_angle is not None else "", alert if alert else ""])
        # also push to Firebase
        if self.firebase_ref:
            payload = {
        "timestamp": ts,
        "ear": ear,
        "total_blinks": total_blinks,
        "blinks_last_min": blinks_last_min,
        "posture_angle": posture_angle,
        "alert": alert,
        }
        try:
            push_log(self.firebase_ref, payload)
        except Exception as e:
            print("Firebase push failed:", e)
     
