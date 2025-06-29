import smtplib
from email.message import EmailMessage

from celery import shared_task

from my_service.core.config import SMTP_HOST, SMTP_PORT


@shared_task
def send_registration_email(to_email: str):
    msg = EmailMessage()
    msg["Subject"] = "Регистрация прошла успешно"
    msg["From"] = "no-replay@example.com"
    msg["To"] = to_email
    msg.set_content("Добро пожаловать! Ваша регистрация прошла успешно.")

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.send_message(msg)

