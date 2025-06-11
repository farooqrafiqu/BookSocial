# BookSocial – Advanced Social-Media Style Book Platform

A Django 5 + DRF project that lets users publish PDF books, like & comment, manage
friends, chat privately, and receive real-time notifications.

---

## Features

| Module | Highlights |
|--------|------------|
| **Auth** | Custom user model, JWT auth, OTP sign-up (Redis cache) |
| **Books** | Upload single PDF or batch (Celery worker), public list & detail |
| **Social** | Likes (duplicate guard), threaded comments, web-socket notifications |
| **Friends** | Friend requests / accept / reject, symmetrical friendships |
| **Messages** | Private chat between friends only |
| **Profile** | Total likes, books shared, editable name & avatar |
| **Tasks** | `/api/tasks/<task_id>/` to poll background jobs |

---

## Local Development


git clone <repo-url> && cd BookSocial
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt

## Environment variables (.env)

DEBUG=True
SECRET_KEY=change-me

# PostgreSQL
POSTGRES_DB=your_db
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_db_password
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432

# Redis
REDIS_URL=redis://127.0.0.1:6379/0

## Redis (Docker)
docker pull redis
docker run -d --name redis -p 6379:6379 redis:latest

## Migrate & create a superuser
python manage.py migrate
python manage.py createsuperuser

## run server

# Terminal 1 – Django + Channels
python manage.py runserver

# Terminal 2 – Celery worker
celery -A core worker -l info
