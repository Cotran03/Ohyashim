from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from users.users import get_user_connection

admin = Blueprint('admin', __name__, url_prefix='/admin')

def is_admin_user(email):
    conn = get_user_connection()
    cur = conn.cursor()
    cur.execute("SELECT is_admin FROM users WHERE email=?", (email,))
    row = cur.fetchone()
    conn.close()
    return row and row[0] == 1

@admin.before_request
def admin_auth_check():
    user_email = session.get('user')
    if not user_email or not is_admin_user(user_email):
        flash("관리자 권한이 필요합니다.")
        return redirect(url_for('auth.login'))

@admin.route('/', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        # 특정 사용자 fingerprint 초기화
        target_email = request.form.get('target_email')
        if target_email:
            conn = get_user_connection()
            cur = conn.cursor()
            cur.execute("SELECT id FROM users WHERE email=?", (target_email,))
            if cur.fetchone():
                cur.execute("UPDATE users SET fingerprint=NULL WHERE email=?", (target_email,))
                conn.commit()
                flash(f"{target_email} 사용자의 fingerprint가 초기화되었습니다.")
            else:
                flash("해당 이메일 사용자가 존재하지 않습니다.")
            conn.close()
        else:
            flash("이메일을 입력해주세요.")

    return render_template('admin_dashboard.html')