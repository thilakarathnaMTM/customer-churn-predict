# Quick run

Needs Python 3.11+ and Node 20+. On Windows use Git Bash.

## One command

```
./start.sh
```

Opens two terminals (backend, frontend). On first run it creates `backend/.venv`, installs
Python and npm packages, trains the model if `mlpart/artifacts/` is empty, seeds the database
and the admin user. Later runs skip anything already done.

- App: http://localhost:5173
- API docs: http://localhost:8000/docs
- Login: `ADMIN_SEED_USERNAME` / `ADMIN_SEED_PASSWORD` from `backend/.env`

`backend/.env`:
```
ML_ARTIFACT_DIR=../mlpart/artifacts
JWT_SECRET=change-me
ADMIN_SEED_USERNAME=erandi
ADMIN_SEED_PASSWORD=erandi123
```
`frontend/.env` already points at the API: `VITE_API_BASE_URL=http://localhost:8000`.

## Manual steps

```
# backend
cd backend
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process # Do this always
python -m venv .venv
source .venv/Scripts/activate      # Windows Git Bash; use .venv/bin/activate on Mac/Linux
pip install -r requirements.txt
python ../mlpart/train.py          # only if mlpart/artifacts/ is missing
python -m app.seed                 # add --reset to rebuild the customers table
python -m app.seed_admin
uvicorn app.main:app --reload --port 8000

# frontend (second terminal)
cd frontend
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process # Do this always
npm install
npm run dev
```

How it connects: the frontend calls the backend at `VITE_API_BASE_URL`; the backend loads the
model from `ML_ARTIFACT_DIR` (written by `mlpart/train.py`).

## Retrain

```
cd backend && source .venv/Scripts/activate && python ../mlpart/train.py && python -m app.seed --reset
```
