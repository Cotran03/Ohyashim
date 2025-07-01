import smtplib
from email.mime.text import MIMEText
from config import SMTP_EMAIL, SMTP_PASSWORD

def send_verification_email(to_email, code):
    """
    인증 이메일을 발송하는 함수.
    이메일 제목, 내용, 수신자, 발신자 정보를 설정하고 SMTP 서버를 통해 전송한다.
    """
    msg = MIMEText(f"인증 코드는 다음과 같습니다: {code}")
    msg['Subject'] = "자율학습 출석 시스템 - 이메일 인증 코드"
    msg['From'] = SMTP_EMAIL
    msg['To'] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)
