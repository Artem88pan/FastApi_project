# 📚 Marketplace Blog Service на FastAPI

> REST-сервис-блог-маркетплейс с категориями и статьями, загрузкой файлов, JWT-аутентификацией и email-уведомлениями через Celery.

---

## 📝 Описание

Marketplace Blog Service позволяет:

- Регистрировать и аутентифицировать пользователей (JWT).  
- Создавать, редактировать и удалять **категории** статей.  
- Создавать, редактировать и удалять **статьи** с возможностью загрузки изображений в MinIO.  
- Запрашивать и сбрасывать пароль по email через Celery + MailHog.  
- Автодокументация Swagger/OpenAPI.

---

## 🛠 Технологии

- **Python 3.10+**, FastAPI  
- **SQLAlchemy 2** + Alembic  
- **PostgreSQL**, **SQLite** (для тестов)  
- **Redis**, **Celery**  
- **MinIO** (S3-совместимое хранилище)  
- **MailHog**  
- **Pydantic V2**

---

## 📂 Требования
- Python 3.10+  
- Docker & Docker Compose v2+  
- Git 

## 📂 Структура проекта
FastAPI_project/
├── Dockerfile
├── docker-compose.yml
├── README.md
├── requirements.txt
├── env.docker.example
├── .env.example
├── src/
│ └── my_service/
│ ├── api/v1/ # роуты: auth, users, categories, articles
│ ├── core/ # настройки, CORS, константы
│ ├── db/ # session, Base
│ ├── models/ # SQLAlchemy-модели
│ ├── schemas/ # Pydantic-схемы
│ ├── main.py # точка входа
│ ├── celery_app.py # инициализация Celery
│ └── tasks.py # фоновые задачи (email)
└── tests/ # pytest + SQLite


## 📂 Переменные окружения
Файл .env.example
Переименуйте в .env и подставьте свои значения.

Файл .env.docker.example
Переименуйте в .env.docker и подставьте свои значения (соответствует настройкам в docker-compose.yml).

## 📂 Запуск локально
1.Клонировать и перейти в папку:
    git clone https://github.com/Artem88pan/FastApi_project.git
    cd marketplace-blog
2.Создать виртуальное окружение:
    python -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt

## 📂 запуск Celery:
celery -A my_service.celery_app:celery_app worker --loglevel=info


## 📂 Запуск Docker
1.Убедитесь, что Docker и Docker Compose установлены.
2.Запустите сервисы:
    docker compose up -d --build
3.Откройте:
    API: http://localhost:8000/docs
    MinIO UI: http://localhost:9000
    MailHog UI: http://localhost:8025


## 📂 Документация API
Метод	   Путь	                        Описание
POST	/auth/register	            Регистрация пользователя
POST	/auth/login	                Вход (JWT)
POST	/auth/request-password	    Запрос ссылки для сброса пароля
POST	/auth/reset-password	    Сброс пароля
GET	    /categories/	            Список категорий
POST	/categories/	            Создать категорию
PUT	    /categories/{id}	        Обновить категорию
DELETE	/categories/{id}	        Удалить категорию
GET 	/articles/	                Список статей
POST	/articles/	                Создать статью (с изображением в MinIO)
GET	    /articles/{id}	            Детали статьи
PUT 	/articles/{id}	            Обновить статью
DELETE	/articles/{id}	            Удалить статью


## 📂 Тестирование
    pytest --cov=src/my_service
Все тесты используют SQLite в памяти

