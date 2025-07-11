from fastapi import Depends

from my_service.core.storage import MinioStorage


def get_storage():
    return MinioStorage()

storage_dep = Depends(get_storage)