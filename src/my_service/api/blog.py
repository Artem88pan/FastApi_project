# src/my_service/api/blog.py

from datetime import datetime, timezone
from typing import List, Optional
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Path,
    Query,
    UploadFile,
    status,
)
from sqlmodel import Session, func, select

from my_service.core.config import MAX_PAGE_SIZE
from my_service.core.deps import storage_dep
from my_service.core.storage import MinioStorage
from my_service.db.session import get_session
from my_service.models.blog import Article, Category, DeletedArticle
from my_service.schemas.blog import (
    ArticleListResponse,
    ArticleRead,
    CategoryCreate,
    CategoryRead,
)

router = APIRouter(prefix="/blog", tags=["blog"])

_required_image = File(...)
_optional_image = File(None)
_search_query = Query(
    None,
    description="Полнотекстовый поиск по title и content"
)
_category_id_query = Query(
    None,
    description="Фильтрация по ID категории"
)
page_number_query = Query(
    1,
    ge=1,
    description="Номер страницы начиная с 1"
)
_page_size_query = Query(
    10,
    ge=1,
    le=MAX_PAGE_SIZE,
    description="размер страницы"
)
_content_form = Form(...)
_category_form = Form(...)
_category_id_form = Form(...)
_title_form = Form(...)
_some_id_path = Path(..., title="ID объекта")
session_dep = Depends(get_session)
storage_dep = storage_dep  # MinioStorage


@router.get(
    "/categories/",
    response_model=List[CategoryRead],
    summary="Список всех категорий",
)
def list_categories(session: Session = session_dep):
    return session.exec(select(Category)).all()


@router.post(
    "/categories",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новую категорию",
)
def create_category(
    data: CategoryCreate,
    session: Session = session_dep,
):
    exists = session.exec(
        select(Category).where(Category.name == data.name)  # type: ignore[arg-type]
    ).first()
    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Категория уже существует"
        )
    cat = Category(name=data.name)
    session.add(cat)
    session.commit()
    session.refresh(cat)
    return cat


@router.get(
    "/articles/",
    response_model=ArticleListResponse,
    summary="Список статей: FTS, фильтрация и пагинация",
)
def list_articles(
    search: Optional[str] = _search_query,
    category_id: Optional[int] = _category_id_query,
    page_number: int = page_number_query,
    page_size: int = _page_size_query,
    session: Session = session_dep,
):
    stmt = select(Article)

    if category_id is not None:
        stmt = stmt.where(Article.category_id == category_id)

    if search:
        tsq = func.to_tsquery("russian", func.plainto_tsquery(search))
        stmt = stmt.where(Article.search_vector.op("@@")(tsq))

    total = session.exec(
        stmt.with_only_columns(func.count()).order_by(None)
    ).one()

    # пагинация
    offset = (page_number - 1) * page_size
    results = session.exec(
        stmt.offset(offset).limit(page_size)
    ).all()

    items = [ArticleRead.model_validate(a) for a in results]
    return ArticleListResponse(
        total=total,
        page_number=page_number,
        page_size=page_size,
        items=items,
    )


@router.post(
    "/articles/",
    response_model=ArticleRead,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить новую статью",
)
async def create_article(
    title: str = _content_form,
    content: str = _content_form,
    category_id: int = _category_id_form,
    image: UploadFile = _required_image,
    storage: MinioStorage = storage_dep,
    session: Session = session_dep,
):
    # читаем файл целиком
    data = await image.read()
    # генерим имя в бакете
    ext = image.filename.rsplit(".", 1)[-1]
    object_name = f"{uuid4().hex}.{ext}"
    # заливаем в MinIO и получаем публичный URL
    image_url = storage.upload_object(
        object_name=object_name,
        data=data,
        content_type=image.content_type or "application/octet-stream",
    )

    now = datetime.now(timezone.utc)
    txt = f"{title} {content}"

    # создаём статью, search_vector автоматически вычислится в SQL
    article = Article(
        title=title,
        content=content,
        category_id=category_id,
        image_url=image_url,
        created_at=now,
        updated_at=now,
        search_vector=func.to_tsvector("russian", txt),
    )
    session.add(article)
    session.commit()
    session.refresh(article)
    return article


@router.patch(
    "/articles/{article_id}",
    response_model=ArticleRead,
    summary="Частичное обновление статьи",
)
async def update_article(
    article_id: int = _some_id_path,
    title: Optional[str] = _title_form,
    content: Optional[str] = _content_form,
    category_id: Optional[int] = _category_id_form,
    image: Optional[UploadFile] = _optional_image,
    storage: MinioStorage = storage_dep,
    session: Session = session_dep,
):
    article = session.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Статья не найдена")

    # обновляем картинку, если прислали
    if image:
        data = await image.read()
        ext = image.filename.rsplit(".", 1)[-1]
        object_name = f"{uuid4().hex}.{ext}"
        image_url = storage.upload_object(
            object_name=object_name,
            data=data,
            content_type=image.content_type or "application/octet-stream",
        )
        article.image_url = image_url

    # обновляем поля
    if title is not None:
        article.title = title
    if content is not None:
        article.content = content
    if category_id is not None:
        article.category_id = category_id

    article.updated_at = datetime.now(timezone.utc)
    txt = f"{article.title} {article.content}"
    article.search_vector = func.to_tsvector("russian", txt)

    session.add(article)
    session.commit()
    session.refresh(article)
    return article


@router.delete(
    "/articles/{article_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Ложное удаление статьи",
)
def delete_article(
    article_id: int = _some_id_path,
    session: Session = session_dep,
):
    article = session.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Статья не найдена")

    # сохраняем в удалёнки
    deleted = DeletedArticle(
        original_id=article.id,
        title=article.title,
        content=article.content,
        category_name=article.category.name,
        image_url=article.image_url,
        deleted_at=datetime.now(timezone.utc),
    )
    session.add(deleted)
    session.delete(article)
    session.commit()
    # 204 — без тела
    return
