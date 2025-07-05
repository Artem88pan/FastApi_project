from io import BytesIO

from fastapi import HTTPException
from minio import Minio
from minio.error import S3Error

from my_service.core.config import (
    MINIO_ACCESS_KEY,
    MINIO_BUCKET,
    MINIO_ENDPOINT,
    MINIO_PUBLIC_URL,
    MINIO_SECRET_KEY,
    USE_MINIO,
)


class MinioStorage:
    def __init__(self):
        if not USE_MINIO:
            raise RuntimeError("MinIO storage is disabled")
        self.client = Minio(
            endpoint=MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=False,  # если у вас http, а не https
        )
        # Создаём бакет, если нет
        if not self.client.bucket_exists(MINIO_BUCKET):
            self.client.make_bucket(MINIO_BUCKET)

    def upload_object(
        self,
        object_name: str,
        data: bytes,
        content_type: str
    ) -> str:
        """
        Загружает байты в MinIO, возвращает публичный URL.
        """
        try:
            self.client.put_object(
                bucket_name=MINIO_BUCKET,
                object_name=object_name,
                data=BytesIO(data),
                length=len(data),
                content_type=content_type,
            )
        except S3Error as e:
            raise HTTPException(
                status_code=500,
                detail=f"MinIO upload error: {e}"
            ) from e
        # Возвращаем путь, по которому можно будет скачать файл
        return f"{MINIO_PUBLIC_URL}/{object_name}"
