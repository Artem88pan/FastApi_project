from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from my_service.core.config import ACCESS_TOKEN_EXPIRE_MINUTES
from my_service.core.security import (
    create_access_token,
    create_password_reset_token,
    hash_password,
    verify_password,
    verify_password_reset_token,
)
from my_service.db.session import get_session
from my_service.models.user import User
from my_service.schemas.user import (
    PasswordReset,
    PasswordResetRequest,
    Token,
    UserCreate,
    UserRead,
)
from my_service.tasks import send_password_reset_email, send_registration_email

router = APIRouter(prefix="/auth", tags=["auth"])

session_dep = Depends(get_session)
oauth_form_dep = Depends(OAuth2PasswordRequestForm)

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, session: Session = session_dep):
    existing = session.exec(select(User).where(User.email == user_in.email)).first() # type: ignore[arg-type]
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
    user = session.exec(select(User).where(User.email == form_data.username)).first() # type: ignore[arg-type]
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверные учетные данные")
    token = create_access_token(user.email)

    response.set_cookie("access_token", token, httponly=True, max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    return {"access_token": token}

@router.post(
    "/forgot-password",
    status_code=status.HTTP_200_OK,
    summary="Запросить ссылку для сброса пароля"
)
def forgot_password(
        request: PasswordResetRequest,
        session: Session = session_dep,

):
    user = session.exec(select(User).where(User.email == request.email)).first() # type: ignore[arg-type]
    if user:
        token = create_password_reset_token(user.email)
        send_password_reset_email.delay(user.email, token)
    return {"msg": "Если e-mail зарегистрирован, вы получите письмо для сброса пароля"}

@router.post(
    "/reset-password",
    status_code=status.HTTP_200_OK,
    summary="Сбросить пароль по токену",
)
def reset_password(
    data: PasswordReset,
    session: Session = session_dep,
):
    email = verify_password_reset_token(data.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недействительный или просроченный токен",
        )
    user = session.exec(
        select(User).where(User.email == email)).first() # type: ignore[arg-type]
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )
    user.hashed_password = hash_password(data.new_password)
    session.add(user)
    session.commit()
    return {"msg": "Пароль успешно изменён"}

