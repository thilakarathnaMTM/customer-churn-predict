"""Trains the churn models and writes everything the backend needs to artifacts/.

    python train.py

Pipeline: clean -> merge duplicate categories -> drop duplicate rows -> keep only the
features a user can realistically supply -> split -> (impute + one-hot + model) tuned
with cross-validation -> evaluate once on a held-out test set.
"""

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import shap
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, f1_score, recall_score, roc_auc_score, roc_curve
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from xgboost import XGBClassifier

HERE = Path(__file__).parent
RAW_CSV = HERE / "data" / "churn_raw.csv"
OUT_DIR = HERE / "artifacts"

# The only inputs the app asks for. The 8 dropped columns (gender, login device, payment
# mode, city tier, app hours, coupons, order-amount hike, number of devices) each add under
# 0.7 AUC points and about 1.5 together; we trade that for a short form. See DOCS.md 5.1.
NUMERIC_COLS = [
    "Tenure",
    "Complain",
    "DaySinceLastOrder",
    "CashbackAmount",
    "SatisfactionScore",
    "NumberOfAddress",
    "OrderCount",
    "WarehouseToHome",
]
CATEGORICAL_COLS = ["PreferedOrderCat", "MaritalStatus"]
FEATURE_COLS = NUMERIC_COLS + CATEGORICAL_COLS
TARGET = "Churn"

# The dataset spells the same category several ways ("Phone" vs "Mobile Phone", ...).
CATEGORY_ALIASES = {
    "PreferedOrderCat": {"Mobile": "Mobile Phone"},
}


def load_clean() -> pd.DataFrame:
    df = pd.read_csv(RAW_CSV)
    for col, mapping in CATEGORY_ALIASES.items():
        df[col] = df[col].str.strip().replace(mapping)
    df = df.drop_duplicates(subset=FEATURE_COLS + [TARGET]).reset_index(drop=True)
    return df[["CustomerID", TARGET] + FEATURE_COLS]


def build_pipeline(estimator) -> Pipeline:
    pre = ColumnTransformer(
        [
            ("num", SimpleImputer(strategy="median"), NUMERIC_COLS),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL_COLS),
        ]
    )
    return Pipeline([("pre", pre), ("clf", estimator)])


def main() -> None:
    df = load_clean()
    print(f"{len(df)} rows after dedupe, churn rate {df[TARGET].mean():.3f}")

    X, y = df[FEATURE_COLS], df[TARGET]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Small, regularised grids — enough to stop the trees memorising the training set.
    candidates = {
        "XGBoost": (
            XGBClassifier(
                subsample=0.8,
                colsample_bytree=0.8,
                eval_metric="logloss",
                random_state=42,
                n_jobs=1,
            ),
            {
                "clf__n_estimators": [200, 400],
                "clf__max_depth": [3, 4, 5],
                "clf__learning_rate": [0.03, 0.06],
                "clf__min_child_weight": [1, 3],
                "clf__reg_lambda": [1, 5],
            },
        ),
        "Random Forest": (
            RandomForestClassifier(
                n_estimators=300, class_weight="balanced", n_jobs=-1, random_state=42
            ),
            {
                "clf__max_depth": [6, 8, 10],
                "clf__min_samples_leaf": [5, 10, 20],
            },
        ),
    }

    results, fitted = [], {}
    for name, (estimator, grid) in candidates.items():
        search = GridSearchCV(
            build_pipeline(estimator), grid, scoring="roc_auc", cv=5, n_jobs=-1
        )
        search.fit(X_train, y_train)
        model = search.best_estimator_
        proba = model.predict_proba(X_test)[:, 1]
        pred = (proba >= 0.5).astype(int)
        fpr, tpr, _ = roc_curve(y_test, proba)
        step = max(1, len(fpr) // 60)
        results.append(
            {
                "name": name,
                "cv_roc_auc": round(float(search.best_score_), 4),
                "roc_auc": round(float(roc_auc_score(y_test, proba)), 4),
                "accuracy": round(float(accuracy_score(y_test, pred)), 4),
                "f1": round(float(f1_score(y_test, pred)), 4),
                "recall": round(float(recall_score(y_test, pred)), 4),
                "fpr": [round(float(v), 4) for v in fpr[::step]] + [1.0],
                "tpr": [round(float(v), 4) for v in tpr[::step]] + [1.0],
                "best_params": {k.removeprefix("clf__"): v for k, v in search.best_params_.items()},
            }
        )
        fitted[name] = model
        r = results[-1]
        print(
            f"{name}: cv_auc={r['cv_roc_auc']} test_auc={r['roc_auc']} "
            f"acc={r['accuracy']} f1={r['f1']} recall={r['recall']} {r['best_params']}"
        )

    # Pick on cross-validated AUC (train data only), not on the test set.
    best_name = max(results, key=lambda r: r["cv_roc_auc"])["name"]
    best = fitted[best_name]
    print("Best model:", best_name)

    # Explanations are computed on the model's one-hot columns, then folded back
    # onto the original input each column came from.
    names = best.named_steps["pre"].get_feature_names_out()
    sources = [
        next(c for c in FEATURE_COLS if n.split("__", 1)[1] == c or n.split("__", 1)[1].startswith(c + "_"))
        for n in names
    ]
    explainer = shap.TreeExplainer(best.named_steps["clf"])

    proba_all = best.predict_proba(X)[:, 1]
    print("probability quantiles:", np.round(np.quantile(proba_all, [0.5, 0.75, 0.9, 0.95]), 3))

    OUT_DIR.mkdir(exist_ok=True)
    joblib.dump(best, OUT_DIR / "model.joblib")
    joblib.dump(explainer, OUT_DIR / "shap_explainer.joblib")
    df.to_csv(OUT_DIR / "churn_clean.csv", index=False)

    meta = {
        "best_model": best_name,
        "numeric_cols": NUMERIC_COLS,
        "categorical_cols": CATEGORICAL_COLS,
        "shap_feature_sources": sources,
        "category_options": {c: sorted(df[c].unique().tolist()) for c in CATEGORICAL_COLS},
        "medians": {c: float(df[c].median()) for c in NUMERIC_COLS},
        "models": results,
    }
    (OUT_DIR / "metadata.json").write_text(json.dumps(meta, indent=2))
    print("Saved to", OUT_DIR)


if __name__ == "__main__":
    main()
