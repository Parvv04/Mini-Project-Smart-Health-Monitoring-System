# firebase_logger.py
import firebase_admin
from firebase_admin import credentials, db
import os

def init_firebase(json_path="firebase_config.json",
                  db_url="https://smart-health-monitor-29524-default-rtdb.asia-southeast1.firebasedatabase.app/"):
    """Initializes Firebase app and returns a reference to /health_logs node."""
    if not os.path.exists(json_path):
        raise FileNotFoundError("Place your service account JSON as firebase_config.json")

    # Initialize only once
    if not firebase_admin._apps:
        cred = credentials.Certificate(json_path)
        firebase_admin.initialize_app(cred, {"databaseURL": db_url})

    ref = db.reference("/health_logs")
    return ref

def push_log(ref, payload):
    """Pushes one log entry to Firebase."""
    ref.push(payload)
