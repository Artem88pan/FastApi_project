from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from my_service.core.config import ACCESS_TOKEN_EXPIRE_MINUTES
from my_service.core.security import create_access_token, hash_password, verify_password
from my_service.db.session import get_session
from my_service.models.user import User
from my_service.schemas.user import Token, UserCreate, UserRead
from my_service.tasks import send_registration_email

router = APIRouter(prefix="/auth", tags=["auth"])

session_dep = Depends(get_session)
oauth_form_dep = Depends(OAuth2PasswordRequestForm)

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, session: Session = session_dep):
    existing = session.exec(select(User).where(User.email == user_in.email)).first()
    if existing:
        raise  HTTPException(status_code=400, detail="Email уже зарегистрирован")

    user = User(email=user_in.email, hashed_password=hash_password(user_in.password))
    session.add(user)
    session.commit()
    session.refresh(user)
    send_registration_email.delay(user.email)
    return user

@router.post("/login", response_model=Token)
def login(
        response: Response,
        form_data: OAuth2PasswordRequestForm = oauth_form_dep,
        session: Session = session_dep
):
    user = session.exec(select(User).where(User.email == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверные учетные данные")
    token = create_access_token(user.email)

    response.set_cookie("access_token", token, httponly=True, max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    return {"access_token": token}

