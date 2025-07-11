import pytest
from fastapi import status
from sqlmodel import select

from my_service.models.blog import Article, Category


def test_list_categories_empty(client):
    resp = client.get("/blog/categories/")
    assert resp.status_code == 200
    assert resp.json() == []

def test_create_category(client, override_get_session):
    payload = {"name": "Новости"}
    resp = client.post("/blog/categories/", json=payload)
    assert resp.status_code == status.HTTP_201_CREATED
    data = resp.json()
    assert data["name"] == "Новости"
    assert "id" in data

    session = next(iter(client.app.dependency_overrides.values()))()
    cat = session.exec(select(Category).where(Category.name == "Новости")).one()
    assert cat.name == "Новости"

def test_create_duplicate_category(client):
    client.post("/blog/categories/", json={"name": "Тест"})
    resp2 = client.post("/blog/categories/", json={"name": "Тест"})
    assert resp2.status_code == status.HTTP_400_BAD_REQUEST
    assert "detail" in resp2.json()

def test_list_articles_empty(client):
    resp = client.get("/blog/articles/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 0
    assert body["items"] == []

def create_article(client):
    cat_resp = client.post("/blog/categories/", json={"name": "Бизнес"})
    cat_id = cat_resp.json()["id"]

    art_payload = {
        "title": "Новая статья",
        "content": "Текст статьи …",
        "category_id": cat_id,
        "image_url": None
    }
    resp = client.post("/blog/articles/", json=art_payload)
    assert resp.status_code == status.HTTP_201_CREATED

    art_data = resp.json()
    assert art_data["title"] == "Новая статья"
    assert art_data["content"].startswith("Текст статьи")
    assert art_data["category"]["id"] == cat_id
    assert "id" in art_data

    session = next(iter(client.app.dependency_overrides.values()))()
    art = session.exec(select(Article).where(Article.id == art_data["id"])).one()
    assert art.title == "Новая статья"


@pytest.mark.parametrize("bad_payload, code", [
    ({"content": "Тест", "category_id": 1}, status.HTTP_422_UNPROCESSABLE_ENTITY),
])
def test_create_article_invalid(client, bad_payload, code):
    resp = client.post("/blog/articles/", json=bad_payload)
    assert resp.status_code == code
