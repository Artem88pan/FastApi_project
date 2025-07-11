import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = (
    f"postgresql://{os.getenv('DATABASE_USER')}:"
    f"{os.getenv('DATABASE_PASSWORD')}@"
    f"{os.getenv('DATABASE_HOST')}:{os.getenv('DATABASE_PORT')}/"
    f"{os.getenv('DATABASE_NAME')}"
)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
STATIC_UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")

SECRET_KEY = os.getenv('SECRET_KEY', 'super-secret-key')
ALGORITHM = os.getenv('ALGORITHM', 'HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 60))
PASSWORD_RESET_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("PASSWORD_RESET_TOKEN_EXPIRE_MINUTES", 15)
)
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
MAX_PAGE_SIZE = int(os.getenv("MAX_PAGE_SIZE", "50"))

SMTP_HOST = os.getenv('SMTP_HOST', 'localhost')
SMTP_PORT = int(os.getenv('SMTP_PORT', 1025))
SMTP_USER = os.getenv('SMTP_USER', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
EMAIL_FROM = os.getenv("EMAIL_FROM")
USE_MINIO = True

MINIO_ENDPOINT     = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY   = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY   = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET       = os.getenv("MINIO_BUCKET",   "blog")
MINIO_SECURE       = os.getenv("MINIO_SECURE",   "false").lower() in ("1","true","yes")
MINIO_PUBLIC_URL = os.getenv(
    "MINIO_PUBLIC_URL",
    f"http://{MINIO_ENDPOINT}/{MINIO_BUCKET}"
)