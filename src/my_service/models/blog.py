from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import Column, Text
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlmodel import Field, Relationship, SQLModel


class Category(SQLModel, table=True):
    __tablename__ = "category"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column("name", Text, nullable=False, unique=True))
    articles: List["Article"] = Relationship(back_populates="category")

class Article(SQLModel, table=True):
    __tablename__ = "article"
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(sa_column=Column("title", Text, nullable=False))
    content: str = Field(sa_column=Column("content", Text, nullable=False))
    category_id: int = Field(foreign_key="category_id", nullable=False)
    image_url: Optional[str] = Field(default=None, sa_column=Column("image_url", Text))
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column("created_at", nullable=False)
    )
    update_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column("update_at", nullable=False)
    )
    search_vector: Optional[str] = Field(default=None, sa_column=Column("search_vector", TSVECTOR))
    category: Optional[Category] = Relationship(back_populates="articles")


class DeletedArticle(SQLModel, table=True):

    __tablename__ = "deleted_article"

    id: Optional[int] = Field(default=None, primary_key=True)
    original_id: int = Field(nullable=False)
    title: str = Field(sa_column=Column("title", Text, nullable=False))
    content: str = Field(sa_column=Column("content", Text, nullable=False))
    category_name: str = Field(sa_column=Column("category_name", Text, nullable=False))
    image_url: Optional[str] = Field(default=None, sa_column=Column("image_url", Text))
    deleted_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column("deleted_at", nullable=False)
    )