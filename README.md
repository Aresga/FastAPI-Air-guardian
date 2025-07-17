# FastAPI-Air-guardian


poetry run uvicorn main:app --reload --host
docker run -d -p 6379:6379 redis
poetry run celery -A celery_app worker --loglevel=info
poetry run celery -A celery_app beat --loglevel=info

docker run --name air-guardian-db -e POSTGRES_USER=agaga -e POSTGRES_PASSWORD=my*password13779 -p 5432:5432 -d postgres

DATABASE_URL="postgresql+asyncpg://agaga:my*password13779@localhost:5432/agaga"