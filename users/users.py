import sqlite3
from config import USER_DB_PATH

def init_user_db():
    """
    사용자 DB 초기화 함수.
    users 테이블이 없으면 생성함.
    fingerprint 컬럼은 처음부터 UNIQUE로 생성 가능.
    """
    conn = sqlite3.connect(USER_DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            fingerprint TEXT UNIQUE
        )
    ''')
    conn.commit()
    conn.close()

def add_fingerprint_column():
    """
    기존 users 테이블에 fingerprint 컬럼이 없으면 추가하는 함수.
    SQLite 제약으로 인해 UNIQUE 없이 추가하고, 애플리케이션에서 중복 관리.
    """
    conn = sqlite3.connect(USER_DB_PATH)
    c = conn.cursor()

    # 테이블 구조 확인
    c.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in c.fetchall()]

    # fingerprint 컬럼이 없으면 추가
    if "fingerprint" not in columns:
        c.execute("ALTER TABLE users ADD COLUMN fingerprint TEXT")
        conn.commit()

    conn.close()

def get_user_connection():
    """
    사용자 DB 연결 반환 함수.
    """
    return sqlite3.connect(USER_DB_PATH)

def init_verification_codes_db():
    """
    이메일 인증코드 저장 테이블 초기화 함수.
    """
    conn = get_user_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS verification_codes (
            email TEXT PRIMARY KEY,
            code TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# 앱 시작 시 수동 테스트용 실행
if __name__ == "__main__":
    init_user_db()
    add_fingerprint_column()
    init_verification_codes_db()