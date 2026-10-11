from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.ml.artifacts import get_artifacts
from app.routers import auth, customers, dashboard, public


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    artifacts = get_artifacts()
    best = next(m for m in artifacts.models if m["name"] == artifacts.best_model_name)
    print(
        f"[startup] Loaded model '{artifacts.best_model_name}' "
        f"(test AUC {best['roc_auc']}, accuracy {best['accuracy']}) from {settings.ML_ARTIFACT_DIR} "
        f"- inputs: {', '.join(artifacts.feature_cols)}"
    )
    yield


app = FastAPI(title="Churn Prediction Dashboard API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(customers.router)
app.include_router(public.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/model-info")
def model_info():
    """Proof of what is answering: the loaded model, its test metrics and its inputs."""
    a = get_artifacts()
    best = next(m for m in a.models if m["name"] == a.best_model_name)
    return {
        "model": a.best_model_name,
        "test_roc_auc": best["roc_auc"],
        "test_accuracy": best["accuracy"],
        "inputs": a.feature_cols,
        "artifact_dir": settings.ML_ARTIFACT_DIR,
    }
