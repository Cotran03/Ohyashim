from datetime import datetime, time
from config import TEST_MODE

SESSIONS = [
    {"name": "오자 1", "start": time(16, 20), "end": time(17, 10), "attendance_start": time(16, 55)},
    {"name": "오자 2", "start": time(17, 20), "end": time(18, 10), "attendance_start": time(17, 55)},
    {"name": "야자",   "start": time(19, 0),  "end": time(20, 40), "attendance_start": time(20, 25)},
]

def get_current_session():
    if TEST_MODE:
        return "오자 1" 

    now = datetime.now().time()
    for session in SESSIONS:
        if session["attendance_start"] <= now <= session["end"]:
            return session["name"]
    return None
