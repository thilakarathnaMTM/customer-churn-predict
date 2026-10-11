import json
from functools import lru_cache
from pathlib import Path

import joblib

from app.config import settings


class MLArtifacts:
    """Everything train.py (mlpart/) writes: the fitted pipeline, SHAP explainer and metadata."""

    def __init__(self):
        artifact_dir = Path(settings.ML_ARTIFACT_DIR)

        self.model = joblib.load(artifact_dir / "model.joblib")
        self.shap_explainer = joblib.load(artifact_dir / "shap_explainer.joblib")
        self.clean_csv_path = artifact_dir / "churn_clean.csv"

        with open(artifact_dir / "metadata.json") as f:
            self.meta = json.load(f)

        self.numeric_cols: list[str] = self.meta["numeric_cols"]
        self.categorical_cols: list[str] = self.meta["categorical_cols"]
        self.feature_cols = self.numeric_cols + self.categorical_cols
        self.shap_feature_sources: list[str] = self.meta["shap_feature_sources"]
        self.medians: dict[str, float] = self.meta["medians"]
        self.category_options: dict[str, list[str]] = self.meta["category_options"]
        self.models: list[dict] = self.meta["models"]
        self.best_model_name: str = self.meta["best_model"]


@lru_cache
def get_artifacts() -> MLArtifacts:
    return MLArtifacts()
