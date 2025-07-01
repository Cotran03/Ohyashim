SECRET_KEY = '01c0abaf3ffae6844b19a2ece4e41b9b6966b73fca4ad210'

ALLOWED_IPS = [

]

TEST_MODE = True

DB_PATH = "db/attendance_test.db" if TEST_MODE else "db/attendance.db"
USER_DB_PATH = "db/test_users.db" if TEST_MODE else "db/users.db"

SCHOOL_EMAIL_DOMAIN = "jungdong.hs.kr"
SMTP_EMAIL = "2410525@jungdong.hs.kr"
SMTP_PASSWORD = "pkrz pxcw udir bxkk"