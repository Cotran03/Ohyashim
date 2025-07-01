import sqlite3

DB_PATH = "db/attendance_test.db"  # 실제 경로로 변경하세요

def init_test_db():
    """
    테스트용 DB 초기화 함수.
    기존 users, verification_codes 테이블을 삭제 후 새로 생성.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 기존 테이블 삭제 (테스트용이라 위험 없음)
    c.execute("DROP TABLE IF EXISTS users;")
    c.execute("DROP TABLE IF EXISTS verification_codes;")
    
    # users 테이블 새로 생성
    c.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            fingerprint TEXT UNIQUE
        );
    ''')
    
    # verification_codes 테이블 새로 생성
    c.execute('''
        CREATE TABLE verification_codes (
            email TEXT PRIMARY KEY,
            code TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    ''')

    conn.commit()
    conn.close()
    print("테스트 DB 초기화 완료")

init_test_db()