from sqlmodel import select
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from my_service.core.security import decode_access_token
from my_service.db.session import get_session
from my_service.models.user import User


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request.state.user = None
        token = request.cookies.get("access_token")
        if token:
            email = decode_access_token(token)
            if email:
                session = next(get_session())
                user = session.exec(select(User).where(User.email == email)).first()
                request.state.user = user
        return await call_next(request)


