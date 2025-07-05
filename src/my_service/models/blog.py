from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import DDL, Column, ColumnElement, DateTime, Index, Text, event
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlmodel import Field, Relationship, SQLModel


class Category(SQLModel, table=True):
    __tablename__ = "category"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column("name", Text, nullable=False, unique=True))
    articles: List["Article"] = Relationship(back_populates="category")
    model_config = {
        "arbitrary_types_allowed": True,
        "from_attributes": True
    }


class Article(SQLModel, table=True):
    __tablename__ = "article"
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(sa_column=Column("title", Text, nullable=False))
    content: str = Field(sa_column=Column("content", Text, nullable=False))
    category_id: int = Field(foreign_key="category.id", nullable=False)
    image_url: Optional[str] = Field(default=None, sa_column=Column("image_url", Text))
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            "created_at",
            DateTime(timezone=True),
            nullable=False
        ),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            "updated_at",
            DateTime(timezone=True),
            nullable=False
        ),
    )

    search_vector: Optional[ColumnElement] = Field(
        default=None,
        sa_column=Column("search_vector", TSVECTOR),
    )
    category: Optional[Category] = Relationship(back_populates="articles")
    model_config = {
        "arbitrary_types_allowed": True,
        "from_attributes": True
    }
    __table_args__ = (
        Index("ix_article_search_vector", "search_vector", postgresql_using="gin"),
    )

SEARCH_VECTOR_TRIGGER = DDL(
    """
    CREATE FUNCTION article_search_vector_update() RETURNS trigger AS $$
    BEGIN
      NEW.search_vector :=
        to_tsvector('russian', coalesce(NEW.title, '') || ' ' || coalesce(NEW.content, ''));
      RETURN NEW;
    END
    $$ LANGUAGE plpgsql;

    CREATE TRIGGER trg_article_search_vector
      BEFORE INSERT OR UPDATE
      ON article
      FOR EACH ROW EXECUTE PROCEDURE article_search_vector_update();
    """
)


event.listen(Article.__table__, 'after_create', SEARCH_VECTOR_TRIGGER)


class DeletedArticle(SQLModel, table=True):

    __tablename__ = "deleted_article"

    id: Optional[int] = Field(default=None, primary_key=True)
    original_id: int = Field(nullable=False)
    title: str = Field(sa_column=Column("title", Text, nullable=False))
    content: str = Field(sa_column=Column("content", Text, nullable=False))
    category_name: str = Field(sa_column=Column("category_name", Text, nullable=False))
    image_url: Optional[str] = Field(default=None, sa_column=Column("image_url", Text))
    deleted_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            "deleted_at",
            DateTime(timezone=True),
            nullable=True
        )
    )