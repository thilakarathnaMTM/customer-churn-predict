import numpy as np
import pandas as pd

from app.config import settings
from app.ml.artifacts import MLArtifacts
from app.ml.features import NON_REASON_COLS, VALUE_AWARE_LABELS


def risk_level(prob: float) -> str:
    if prob >= settings.RISK_THRESHOLD_HIGH:
        return "high"
    if prob >= settings.RISK_THRESHOLD_MEDIUM:
        return "medium"
    return "low"


# SHAP values are in log-odds; contributions below this are noise and not reported.
MIN_REASON_SHAP = 0.1


def _fmt(value: float) -> str:
    return f"{value:g}" if float(value).is_integer() else f"{value:.1f}"


def describe_feature(feat: str, value, medians: dict[str, float]) -> str:
    """Label that matches the customer's actual value, not a fixed assumption."""
    if feat == "Complain":
        return "complaint filed" if value and float(value) > 0 else "no complaint filed"
    if feat == "PreferedOrderCat":
        return f"preferred order category ({value})"
    low, high, unit = VALUE_AWARE_LABELS[feat]
    label = low if float(value) <= medians[feat] else high
    return f"{label} ({_fmt(float(value))}{unit})"


def _churn_shap(explainer, X: pd.DataFrame) -> np.ndarray:
    """SHAP values for the churn class, shape (n_rows, n_transformed_features)."""
    values = explainer.shap_values(X)
    if isinstance(values, list):
        return np.asarray(values[1])
    values = np.asarray(values)
    return values[:, :, 1] if values.ndim == 3 else values


def reason_impacts_for_row(
    shap_row: np.ndarray, raw_row: pd.Series, artifacts: MLArtifacts, n: int = 5
) -> list[dict]:
    """Top-n inputs pushing this row toward churn. One-hot columns are folded back onto
    their source input; impact_pct is that input's share of the total churn-pushing weight."""
    per_feature: dict[str, float] = {}
    for src, val in zip(artifacts.shap_feature_sources, shap_row):
        per_feature[src] = per_feature.get(src, 0.0) + float(val)

    positive = [(f, v) for f, v in per_feature.items() if v > 0 and f not in NON_REASON_COLS]
    total = sum(v for _, v in positive) or 1.0
    positive.sort(key=lambda t: t[1], reverse=True)

    return [
        {
            "label": describe_feature(feat, raw_row[feat], artifacts.medians),
            "impact_pct": round(v / total * 100, 1),
        }
        for feat, v in positive[:n]
        if v >= MIN_REASON_SHAP
    ]


def predict_and_explain(raw_rows: pd.DataFrame, artifacts: MLArtifacts) -> list[dict]:
    """Scores a frame of customers (one column per model input). Batched so seeding
    5k customers is one model/SHAP call rather than thousands."""
    X = raw_rows[artifacts.feature_cols]
    probs = artifacts.model.predict_proba(X)[:, 1]
    X_t = artifacts.model.named_steps["pre"].transform(X)
    shap_values = _churn_shap(artifacts.shap_explainer, X_t)

    out = []
    for i, prob in enumerate(probs):
        # A low-risk customer has nothing to be warned about: individual factors may push
        # up a little, but the overall probability is small, so listing them misleads.
        level = risk_level(float(prob))
        impacts = (
            [] if level == "low" else reason_impacts_for_row(shap_values[i], X.iloc[i], artifacts)
        )
        out.append(
            {
                "churn_probability": float(prob),
                "risk_level": level,
                "top_reasons": [r["label"] for r in impacts],
                "reason_impacts": impacts,
            }
        )
    return out
