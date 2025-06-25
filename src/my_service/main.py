from fastapi import FastAPI

from my_service.api import items

app = FastAPI(
    title = 'My service',
    description = 'Блог маркетплейса',
    version  = '0.1.0'
)

app.include_router(items.router)