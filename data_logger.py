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

    def log(self, ear, total_blinks, blinks_last_min, posture_angle, alert):
        ts = datetime.now().isoformat()
        with open(self.csv_path, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([ts, ear if ear is not None else "", total_blinks, blinks_last_min, posture_angle if posture_angle is not None else "", alert if alert else ""])
