from typing import Optional

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "user"
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Уникальный идентификатор пользователя"
    )
    email: str = Field(
        index=True,
        sa_column_kwargs={"unique": True, "nullable": False},
        description="Электронная почта, используется как логин"
    )
    hashed_password: str = Field(
        nullable=False,
        description="Хеш пароля, никогда не храним пароль в явном виде"
    )
    is_active: bool = Field(
        default=True,
        description="Флаг, показывающий, активна ли учетная запись"
    )