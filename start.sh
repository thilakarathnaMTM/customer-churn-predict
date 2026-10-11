#!/usr/bin/env bash
# Starts backend (FastAPI :8000) and frontend (Vite :5173), each in its own terminal.
#   ./start.sh            open both terminals
#   ./start.sh backend    run only the backend in this terminal
#   ./start.sh frontend   run only the frontend in this terminal
# Installs the venv / node_modules only if they are missing.
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"

backend() {
  cd "$ROOT/backend"
  [ -f .env ] || { cp .env.example .env; echo "Created backend/.env from .env.example - edit it, then re-run."; exit 1; }

  if [ ! -d .venv ]; then
    echo ">> Creating Python venv"
    (python3 -m venv .venv 2>/dev/null || python -m venv .venv)
    NEW_VENV=1
  fi
  # shellcheck disable=SC1091
  source .venv/Scripts/activate 2>/dev/null || source .venv/bin/activate
  if [ -n "$NEW_VENV" ]; then
    echo ">> Installing backend requirements"
    pip install -r requirements.txt
  fi

  if [ ! -f "$ROOT/mlpart/artifacts/model.joblib" ]; then
    echo ">> No trained model found, training"
    python "$ROOT/mlpart/train.py"
  fi

  python -m app.seed          # no-op if customers already seeded
  python -m app.seed_admin    # username/password from .env
  uvicorn app.main:app --reload --port 8000
}

frontend() {
  cd "$ROOT/frontend"
  [ -d node_modules ] || { echo ">> Installing frontend packages"; npm install; }
  npm run dev
}

open_terminal() {  # $1 = title, $2 = mode
  local cmd="cd '$ROOT' && ./start.sh $2; exec bash"
  case "$(uname -s)" in
    MINGW*|MSYS*|CYGWIN*) cmd.exe //c start "$1" bash -c "$cmd" ;;
    Darwin) osascript -e "tell application \"Terminal\" to do script \"bash -c \\\"$cmd\\\"\"" >/dev/null ;;
    *) if command -v gnome-terminal >/dev/null; then gnome-terminal --title="$1" -- bash -c "$cmd"
       else x-terminal-emulator -e bash -c "$cmd" & fi ;;
  esac
}

case "${1:-}" in
  backend) backend ;;
  frontend) frontend ;;
  "") open_terminal Backend backend; open_terminal Frontend frontend
      echo "Backend  -> http://localhost:8000/docs"
      echo "Frontend -> http://localhost:5173" ;;
  *) echo "usage: ./start.sh [backend|frontend]"; exit 1 ;;
esac
