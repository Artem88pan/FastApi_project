from fastapi import FastAPI
from starlette.middleware import Middleware

from my_service.api import auth, users
from my_service.core.middleware import AuthMiddleware
from my_service.db.session import init_db

middleware = [
    Middleware(AuthMiddleware)
]
app = FastAPI(
    title = 'My Service',
    description = 'Блог маркетплейса',
    version  = '0.1.0',
    middleware=middleware
)

@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(auth.router)
app.include_router(users.router)