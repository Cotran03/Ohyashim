from flask import Flask, redirect, url_for, render_template, request, abort, flash, session
import ipaddress
import re

from config import ALLOWED_IPS, SECRET_KEY, TEST_MODE
import attendance.attendance as attendance
import attendance.sessions as sessions
import users.users as users
from auth.auth import auth as auth_blueprint
from admin.admin import admin as admin_blueprint

app = Flask(__name__)
app.secret_key = SECRET_KEY

# 허용 IP 네트워크 리스트 (학교 내부망 등)
ALLOWED_NETWORKS = [ipaddress.ip_network(ip) for ip in ALLOWED_IPS]

def is_valid_student_id(student_id: str) -> bool:
    """학번 형식 검사: 5자리 숫자, 1~3학년, 01~08반, 01~99번"""
    if not re.fullmatch(r'\d{5}', student_id):
        return False
    grade = int(student_id[0])
    klass = int(student_id[1:3])
    number = int(student_id[3:])
    return grade in {1, 2, 3} and 1 <= klass <= 8 and 1 <= number <= 99

@app.before_request
def limit_remote_addr():
    """테스트 모드가 아니면 학교 내부 IP 대역이 아니면 접속 차단"""
    if TEST_MODE:
        return
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    try:
        ip_addr = ipaddress.ip_address(ip)
    except ValueError:
        abort(400)
    if not any(ip_addr in net for net in ALLOWED_NETWORKS):
        abort(403)

@app.before_request
def check_login():
    """로그인/회원가입/인증 페이지 및 static 제외, 로그인 안된 경우 로그인 페이지로 리다이렉트"""
    if request.endpoint in {'auth.login', 'auth.register', 'auth.verify', 'static'}:
        return
    if not session.get('user'):
        return redirect(url_for('auth.login'))

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    current_session = sessions.get_current_session()

    if request.method == 'POST':
        if not current_session:
            flash("지금은 출석 가능한 시간이 아닙니다.")
            return redirect(url_for('home'))

        name = request.form.get('name', '').strip()
        student_id = request.form.get('student_id', '').strip()
        fingerprint = request.form.get('fingerprint')
        ip = request.remote_addr

        if not name or not student_id:
            flash("이름 또는 학번이 누락되었습니다.")
            return redirect(url_for('home'))
        
        if not fingerprint:
            flash("오류가 발생했습니다. 다시 시도해 주세요.")
            return redirect(url_for('home'))

        if name.isdigit():
            flash("이름에 숫자만 입력할 수 없습니다.")
            return redirect(url_for('home'))

        if not is_valid_student_id(student_id):
            flash("학번 형식이 올바르지 않습니다.")
            return redirect(url_for('home'))

        if attendance.is_duplicate_fingerprint(student_id, current_session, fingerprint):
            flash("같은 기기에서 여러 명의 출석이 감지되었습니다.")
            return redirect(url_for('home'))

        success = attendance.record_attendance(name, student_id, current_session, ip, fingerprint)
        if success:
            flash(f"{name}님, '{current_session}' 출석이 완료되었습니다.")
        else:
            flash("이미 출석한 기록이 있습니다.")
        return redirect(url_for('home'))

    return render_template('home.html', current_session=current_session)

# 블루프린트 등록
app.register_blueprint(auth_blueprint)
app.register_blueprint(admin_blueprint)

if __name__ == '__main__':
    # DB 초기화 (users 테이블 생성 및 fingerprint 컬럼 추가 - 컬럼 추가 시 UNIQUE 제거)
    users.init_user_db()
    users.add_fingerprint_column()  # UNIQUE 없이 fingerprint 컬럼 추가하도록 수정 필요
    users.init_verification_codes_db()
    attendance.init_db()
    app.run(host='0.0.0.0', port=5000)