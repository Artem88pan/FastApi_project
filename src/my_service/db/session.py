import logging

from sqlmodel import Session, SQLModel, create_engine

from my_service.core.config import DATABASE_URL
from my_service.models.blog import Article, Category, DeletedArticle  # noqa: F401

engine = create_engine(DATABASE_URL, echo=True)

def init_db() -> None:
    SQLModel.metadata.create_all(engine)
    logging.info("Database table create")

def get_session():
    with Session(engine) as session:
        yield session

