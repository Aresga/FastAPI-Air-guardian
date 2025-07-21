
help:
	@echo "Available commands:"
	@echo "  install     - Install dependencies"
	@echo "  setup   - Setup development environment (start DB & Redis)"
	@echo "  start   - Start all services"
	@echo "  stop    - Stop all services"
	@echo "  restart - Restart all services"
	@echo "  logs        - Show logs"
	@echo "  clean       - Clean up containers and logs"
	@echo "  test        - Run tests"

install:
	@echo "🔧 Installing dependencies..."
	@echo "Creating a virtual environment..."
	@poetry env use python3
	@poetry lock || true
	@poetry install


setup:
	@echo "🚀 Setting up development environment..."
	@docker run -d --name air-guardian-redis -p 6379:6379 redis:7-alpine 2>/dev/null || docker start air-guardian-redis
	@docker run -d --name air-guardian-postgres \
		-e POSTGRES_USER=agaga \
		-e POSTGRES_PASSWORD=my*password13779 \
		-e POSTGRES_DB=agaga \
		-p 5432:5432 \
		postgres:15 2>/dev/null || docker start air-guardian-postgres
	@echo "⏳ Waiting for PostgreSQL to be ready..."
	@sleep 5
	@poetry run python -m src.create_tables || \
		(echo "❌ Database setup failed, recreating container..." && make db-reset)
	@echo "🔧 Ensuring database user exists..."
	@docker exec air-guardian-postgres psql -U agaga -d agaga -c "SELECT 1;" 2>/dev/null || \
		(echo "❌ User creation failed, recreating container..." && make db-reset)
	@echo "✅ Development environment ready!"
	

start:
	@echo "🚀 Starting Air Guardian services..."
	@mkdir -p logs .pids
	@echo "🏗️ Creating database tables..."
	@poetry run python -m src.create_tables || (echo "❌ Failed to create tables" && exit 1)
	@echo "🌐 Starting FastAPI..."
	@poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload > logs/fastapi.log 2>&1 & echo $$! > .pids/fastapi.pid
	@echo "👷 Starting Celery Worker..."
	@poetry run celery -A src.celery_app worker --loglevel=info > logs/celery_worker.log 2>&1 & echo $$! > .pids/celery_worker.pid
	@echo "⏰ Starting Celery Beat..."
	@poetry run celery -A src.celery_app beat --loglevel=info > logs/celery_beat.log 2>&1 & echo $$! > .pids/celery_beat.pid
	@sleep 2
	@echo "✅ All services started!"
	@echo "📊 FastAPI: http://localhost:8000"
	@echo "📋 Use 'make logs' to see logs"
	@echo "🛑 Use 'make dev-stop' to stop services"

stop:
	@echo "🛑 Stopping Air Guardian services..."
	@mkdir -p .pids
	@if [ -f .pids/fastapi.pid ]; then kill `cat .pids/fastapi.pid` 2>/dev/null || true; rm .pids/fastapi.pid; fi
	@if [ -f .pids/celery_worker.pid ]; then kill `cat .pids/celery_worker.pid` 2>/dev/null || true; rm .pids/celery_worker.pid; fi
	@if [ -f .pids/celery_beat.pid ]; then kill `cat .pids/celery_beat.pid` 2>/dev/null || true; rm .pids/celery_beat.pid; fi
	@pkill -f "uvicorn main:app" 2>/dev/null || true
	@pkill -f "celery -A celery_app" 2>/dev/null || true
	@echo "✅ All services stopped!"

restart: stop start

logs:
	@echo "📋 Recent logs (Ctrl+C to exit):"
	@echo "==================== FastAPI ===================="
	@tail -f logs/fastapi.log 2>/dev/null &
	@echo "================== Celery Worker ================"
	@tail -f logs/celery_worker.log 2>/dev/null &
	@echo "================== Celery Beat =================="
	@tail -f logs/celery_beat.log 2>/dev/null &
	@wait

beat-reset:
	@echo "🔄 Resetting Celery Beat schedule..."
	@make stop
	@rm -f celerybeat-schedule celerybeat.pid
	@echo "✅ Celery Beat schedule reset complete!"
	
clean: beat-reset
	@echo "🧹 Cleaning up..."
	@make stop
	@docker stop air-guardian-redis air-guardian-postgres 2>/dev/null || true
	@docker rm air-guardian-redis air-guardian-postgres 2>/dev/null || true
	@rm -rf logs .pids
	@rm -rf /.pids /.logs 
	@rm -f celerybeat-schedule celerybeat.pid celerybeat-schedule-shm celerybeat-schedule-wal
	@echo "✅ Cleanup complete!"


# TODO 
test:
	poetry run pytest


db-create:
	@echo "🏗️ Creating database tables..."
	@poetry run python -m src.create_tables
	@echo "✅ Tables created!"

# Database management
db-reset:
	@echo "🔄 Resetting database..."
	@docker stop air-guardian-postgres 2>/dev/null || true
	@docker rm air-guardian-postgres 2>/dev/null || true
	@docker volume rm air-guardian-postgres-data 2>/dev/null || true
	@echo "🚀 Creating fresh PostgreSQL container..."
	@docker run -d --name air-guardian-postgres \
		-e POSTGRES_USER=agaga \
		-e POSTGRES_PASSWORD=my*password13779 \
		-e POSTGRES_DB=agaga \
		-p 5432:5432 \
		-v air-guardian-postgres-data:/var/lib/postgresql/data \
		postgres:15
	@echo "⏳ Waiting for PostgreSQL to initialize..."
	@sleep 15
	@echo "✅ Database reset complete!"

# Quick status check
status:
	@echo "📊 Service Status:"
	@echo "Redis: $$(docker ps --filter name=air-guardian-redis --format 'table {{.Status}}' | tail -n 1 || echo '❌ Not running')"
	@echo "PostgreSQL: $$(docker ps --filter name=air-guardian-postgres --format 'table {{.Status}}' | tail -n 1 || echo ' ❌ Not running')"
	@echo "FastAPI: $$(if [ -f .pids/fastapi.pid ] && kill -0 `cat .pids/fastapi.pid` 2>/dev/null; then echo ' ✅ Running'; else echo '❌ Not running'; fi)"
	@echo "Celery Worker: $$(if [ -f .pids/celery_worker.pid ] && kill -0 `cat .pids/celery_worker.pid` 2>/dev/null; then echo ' ✅ Running'; else echo '❌ Not running'; fi)"
	@echo "Celery Beat: $$(if [ -f .pids/celery_beat.pid ] && kill -0 `cat .pids/celery_beat.pid` 2>/dev/null; then echo ' ✅ Running'; else echo '❌ Not running'; fi)"


.PHONY: help install setup start stop restart logs clean test
