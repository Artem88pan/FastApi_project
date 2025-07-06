# ruff: noqa: E402
import os
import sys

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
)
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

import my_service.tasks as tasks
from my_service.db.session import get_session
from my_service.main import app

TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

@pytest.fixture(scope="session", autouse=True)
def prepare_db():
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(autouse=True)
def override_get_session():
    def _get_test_session():
        return Session(engine)

    app.dependency_overrides[get_session] = _get_test_session
    yield
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def disable_celery(monkeypatch):
    monkeypatch.setattr(tasks.send_registration_email, "delay", lambda *args, **kwargs: None)
    monkeypatch.setattr(tasks.send_password_reset_email, "delay", lambda *args, **kwargs: None)

@pytest.fixture()
def client():
    return TestClient(app)

