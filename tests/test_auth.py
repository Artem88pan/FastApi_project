import pytest
from fastapi import status
from httpx import Response
from sqlmodel import Session, select

from my_service.core.security import create_password_reset_token
from my_service.main import app
from my_service.models.user import User


def register(client, email="test@example.com", password="secret123") -> Response:
    return client.post(
        "/auth/register",
        json={"email": email, "password": password}
    )

def login(client, email="test@example.com", password="secret123") -> Response:
    return client.post(
        "/auth/login",
        data={"username": email, "password": password}
    )

def test_register_and_duplicate(client, override_get_session):
    r1 = register(client)
    assert r1.status_code == status.HTTP_201_CREATED
    body = r1.json()
    assert body["email"] == "test@example.com"
    assert "id" in body
    session: Session = next(iter(app.dependency_overrides.value()))()
    user = session.exec(select(User).where(User.email == "test@example.com")).one()  # type: ignore[arg-type]
    assert user.email == "test@example.com"

    r2 = register(client)
    assert r2.status_code == status.HTTP_400_BAD_REQUEST

def test_login_success_and_cookie(client):
    register(client, email="foo@bar.com", password="passABC1")
    r = login(client, email="foo@bar.com", password="passABC1")
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert "access_token" in data
    sc = r.headers.get("set-cookie", "")
    assert "access_token" in sc
    assert "httponly" in sc.lower()

@pytest.mark.parametrize("email,pw", [
    ("no@one.com", "whatever"),
    ("foo@bar.com", "badpass"),

])
def test_login_fall(client, email, pw):
    r = login(client, email=email, password=pw)
    assert r.status_code == status.HTTP_401_UNAUTHORIZED

def test_forgot_password_always_200(client):
    r1 = client.post("/auth/forgot-password", json={"email": "ghost@nowhere"})
    assert r1.status_code == status.HTTP_200_OK
    r2 = client.post("/auth/forgot-password", json={"email": "test@example.com"})
    assert r2.status_code == status.HTTP_200_OK

def test_reset_password_flow(client):
    register(client, email="zz@zz.zz", password="oldpass")

    token = create_password_reset_token("zz@zz.zz")
    r = client.post(
        "/auth/reset-password",
        json={"token": token, "new_password": "newpass!23"},
    )
    assert r.status_code == status.HTTP_200_OK

    r_old = login(client, email="zz@zz.zz", password="oldpass")
    assert r_old.status_code == status.HTTP_401_UNAUTHORIZED

    r_new = login(client, email="zz@zz.zz", password="newpass!23")
    assert r_new.status_code == status.HTTP_200_OK






