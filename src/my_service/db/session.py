import logging

from sqlalchemy import event
from sqlmodel import Session, SQLModel, create_engine

from my_service.core.config import DATABASE_URL
from my_service.models.blog import SEARCH_VECTOR_TRIGGER, Article
from my_service.models.user import User  # noqa: F401

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
engine = create_engine(DATABASE_URL, echo=True, connect_args=connect_args)

def init_db() -> None:
    SQLModel.metadata.create_all(engine)
    logging.info("Database tables created")

def get_session():
    with Session(engine) as session:
        yield session

# Регистрируем DDL-триггер ТОЛЬКО на настоящем Postgres
if engine.dialect.name == "postgresql":
    event.listen(
        Article.__table__,
        "after_create",
        SEARCH_VECTOR_TRIGGER
    )
