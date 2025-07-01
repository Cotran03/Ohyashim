# auth/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from config import SCHOOL_EMAIL_DOMAIN
from users.users import get_user_connection
from utils.email_utils import send_verification_email
import random

auth = Blueprint('auth', __name__)

def generate_code():
    return str(random.randint(100000, 999999))

def hash_password(password):
    return generate_password_hash(password)

def verify_password(password, hashed):
    return check_password_hash(hashed, password)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        fingerprint = request.form.get('fingerprint')

        if not fingerprint:
            flash("기기 정보가 누락되었습니다. 다시 시도해 주세요.")
            return redirect(url_for('auth.login'))

        conn = get_user_connection()
        cur = conn.cursor()
        cur.execute("SELECT password, fingerprint FROM users WHERE email=?", (email,))
        row = cur.fetchone()

        if not row:
            conn.close()
            flash("이메일 또는 비밀번호가 잘못되었습니다.")
            return redirect(url_for('auth.login'))

        stored_password, stored_fingerprint = row

        if not verify_password(password, stored_password):
            conn.close()
            flash("이메일 또는 비밀번호가 잘못되었습니다.")
            return redirect(url_for('auth.login'))

        # fingerprint 등록 또는 비교
        if stored_fingerprint is None:
            cur.execute("UPDATE users SET fingerprint=? WHERE email=?", (fingerprint, email))
            conn.commit()
        elif stored_fingerprint != fingerprint:
            conn.close()
            flash("등록된 기기에서만 로그인할 수 있습니다.")
            return redirect(url_for('auth.login'))

        conn.close()
        session['user'] = email
        return redirect(url_for('home'))

    return render_template('login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        fingerprint = request.form.get('fingerprint')

        if not email.endswith(f"@{SCHOOL_EMAIL_DOMAIN}"):
            flash("학교 이메일만 사용할 수 있습니다.")
            return redirect(url_for('auth.register'))

        if not fingerprint:
            flash("기기 인증 정보를 수집하지 못했습니다. 다시 시도해 주세요.")
            return redirect(url_for('auth.register'))

        code = generate_code()
        send_verification_email(email, code)

        conn = get_user_connection()
        conn.execute("REPLACE INTO verification_codes (email, code) VALUES (?, ?)", (email, code))
        conn.commit()
        conn.close()

        # 세션에 임시 저장
        session['pending_email'] = email
        session['pending_password'] = hash_password(password)
        session['pending_fingerprint'] = fingerprint

        return redirect(url_for('auth.verify'))

    return render_template('register.html')

@auth.route('/verify', methods=['GET', 'POST'])
def verify():
    if 'pending_email' not in session or 'pending_password' not in session or 'pending_fingerprint' not in session:
        flash("잘못된 접근입니다.")
        return redirect(url_for('auth.register'))

    if request.method == 'POST':
        code_input = request.form.get('code')
        email = session['pending_email']

        conn = get_user_connection()
        cur = conn.cursor()
        cur.execute("SELECT code FROM verification_codes WHERE email=?", (email,))
        row = cur.fetchone()

        if not row or row[0] != code_input:
            flash("인증 코드가 잘못되었습니다.")
            return redirect(url_for('auth.verify'))

        # users 테이블에 fingerprint도 함께 저장
        cur.execute(
            "INSERT INTO users (email, password, fingerprint) VALUES (?, ?, ?)",
            (email, session['pending_password'], session['pending_fingerprint'])
        )
        cur.execute("DELETE FROM verification_codes WHERE email=?", (email,))
        conn.commit()
        conn.close()

        # 세션 정리
        session.pop('pending_email')
        session.pop('pending_password')
        session.pop('pending_fingerprint')
        flash("회원가입이 완료되었습니다. 로그인해주세요.")
        return redirect(url_for('auth.login'))

    return render_template('verify.html')