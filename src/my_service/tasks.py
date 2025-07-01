import smtplib
from email.message import EmailMessage

from celery import shared_task

from my_service.core.config import (
    BASE_URL,
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES,
    SMTP_HOST,
    SMTP_PORT,
    SMTP_USER,
)


@shared_task
def send_registration_email(to_email: str):
    msg = EmailMessage()
    msg["Subject"] = "Регистрация прошла успешно"
    msg["From"] = "no-replay@example.com"
    msg["To"] = to_email
    msg.set_content("Добро пожаловать! Ваша регистрация прошла успешно.")

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.send_message(msg)

@shared_task
def send_password_reset_email(email: str, token: str):
    link = f"{BASE_URL}/reset-password?token={token}"
    msg = EmailMessage()
    msg["Subject"] = "Сброс пароля"
    msg["From"] = SMTP_USER
    msg["To"] = email
    msg.set_content(
        f"Здравствуйте!\n\n"
        f"Чтобы сбросить пароль, перейдите по этой ссылке:\n\n"
        f"{link}\n\n"
        f"Ссылка действительна {PASSWORD_RESET_TOKEN_EXPIRE_MINUTES} мин."
    )
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.send_message(msg)
