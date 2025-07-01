# attendance.py
import sqlite3
from datetime import datetime
from config import DB_PATH

# 출석 DB 초기화 함수
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            name TEXT NOT NULL,
            session TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            ip TEXT,
            fingerprint TEXT,
            suspicious INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

# 출석 기록 함수
def record_attendance(name, student_id, session, ip, fingerprint):
    timestamp = datetime.now().isoformat()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 이미 출석한 경우 중복 방지
    c.execute("SELECT * FROM attendance WHERE student_id=? AND session=?", (student_id, session))
    if c.fetchone():
        conn.close()
        return False

    # 출석 삽입
    c.execute('''
        INSERT INTO attendance (student_id, name, session, timestamp, ip, fingerprint)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (student_id, name, session, timestamp, ip, fingerprint))
    conn.commit()
    conn.close()
    return True

# 대리 출석 여부 확인 함수 (같은 fingerprint로 다른 학번 출석한 경우)
def is_duplicate_fingerprint(student_id, session, fingerprint):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT COUNT(*) FROM attendance 
        WHERE session=? AND fingerprint=? AND student_id != ?
    ''', (session, fingerprint, student_id))
    count = c.fetchone()[0]
    conn.close()
    return count > 0