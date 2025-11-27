#!/usr/bin/env bash

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$PROJECT_ROOT"

PG_CONTAINER="vibecode-jam-postgres"
MAILHOG_CONTAINER="vibecode-jam-mailhog"

function start_postgres() {
  if docker ps -a --format '{{.Names}}' | grep -q "^${PG_CONTAINER}$"; then
    echo "🚀 Postgres container already exists, starting..."
    docker start "$PG_CONTAINER" >/dev/null
  else
    echo "🚀 Running Postgres container..."
    docker run -d \
      --name "$PG_CONTAINER" \
      -e POSTGRES_USER=vibecode_jam \
      -e POSTGRES_PASSWORD=vibecode_jam \
      -e POSTGRES_DB=vibecode_jam \
      -p 5432:5432 \
      -v vibecode-jam-pgdata:/var/lib/postgresql/data \
      postgres:16-alpine >/dev/null
  fi

  echo -n "⏳ Waiting for Postgres to be ready"
  for _ in {1..30}; do
    if docker exec "$PG_CONTAINER" pg_isready -U vibecode_jam >/dev/null 2>&1; then
      echo " ✅"
      return
    fi
    echo -n "."
    sleep 1
  done
  echo " ❌"
  echo "Postgres did not become ready in time."
  exit 1
}

function start_mailhog() {
  if docker ps -a --format '{{.Names}}' | grep -q "^${MAILHOG_CONTAINER}$"; then
    echo "📮 Mailhog container already exists, starting..."
    docker start "$MAILHOG_CONTAINER" >/dev/null
  else
    echo "📮 Running Mailhog container..."
    docker run -d \
      --name "$MAILHOG_CONTAINER" \
      -p 1025:1025 \
      -p 8025:8025 \
      mailhog/mailhog:v1.0.1 >/dev/null
  fi
}

function start_backend() {
  echo "⚙️  Starting backend..."
  pushd backend >/dev/null
  source venv/bin/activate
  export DATABASE_URL=postgresql+asyncpg://vibecode_jam:vibecode_jam@localhost:5432/vibecode_jam
  export SMTP_HOST=localhost
  export SMTP_PORT=1025
  export SMTP_FROM=ide@vibecode.local
  export EXECUTOR_SERVICE_URL=http://localhost:8001
  export ML_SERVICE_URL=http://localhost:8002/api/v1
  export MODERATOR_TOKEN=moderator_secret_token
  python scripts/bootstrap_seed.py
  uvicorn app.main:app --host 0.0.0.0 --port 8000 &
  BACKEND_PID=$!
  popd >/dev/null
}

function start_executor() {
  echo "⚙️  Starting executor..."
  pushd executor >/dev/null
  source venv/bin/activate
  export BACKEND_URL=http://localhost:8000/api
  uvicorn app.main:app --host 0.0.0.0 --port 8001 &
  EXECUTOR_PID=$!
  popd >/dev/null
}

function start_ml() {
  echo "🤖 Starting ML service..."
  pushd ml >/dev/null
  source venv/bin/activate
  uvicorn app.main:app --host 0.0.0.0 --port 8002 &
  ML_PID=$!
  popd >/dev/null
}

function start_frontend() {
  echo "🖥️  Starting frontend..."
  pushd frontend >/dev/null
  npm install
  npm run dev -- --host 0.0.0.0 --port 5173 &
  FRONTEND_PID=$!
  popd >/dev/null
}

function stop_services() {
  echo ""
  echo "🛑 Stopping services..."
  [[ -n "${FRONTEND_PID:-}" ]] && kill "$FRONTEND_PID" 2>/dev/null || true
  [[ -n "${ML_PID:-}" ]] && kill "$ML_PID" 2>/dev/null || true
  [[ -n "${EXECUTOR_PID:-}" ]] && kill "$EXECUTOR_PID" 2>/dev/null || true
  [[ -n "${BACKEND_PID:-}" ]] && kill "$BACKEND_PID" 2>/dev/null || true
  docker stop "$PG_CONTAINER" >/dev/null 2>&1 || true
  docker stop "$MAILHOG_CONTAINER" >/div>null 2>&1 || true
}

trap stop_services EXIT

start_postgres
start_mailhog
start_backend
start_executor
start_ml
start_frontend

echo ""
echo "✅ All services started."
echo "Frontend: http://localhost:5173"
echo "Backend API: http://localhost:8000/docs"
echo "Mailhog: http://localhost:8025"
echo ""
echo "Press Ctrl+C to stop everything."

wait

