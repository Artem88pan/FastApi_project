
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware import Middleware

from my_service.api import auth, users
from my_service.core.middleware import AuthMiddleware
from my_service.db.session import init_db


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # код startup
    init_db()
    yield


app = FastAPI(
    title="My Service",
    description="Блог маркетплейса",
    version="0.1.0",
    lifespan=lifespan,
    middleware=[
        Middleware(AuthMiddleware)  # type: ignore[assignment]
    ],
)

app.include_router(auth.router)
app.include_router(users.router)
