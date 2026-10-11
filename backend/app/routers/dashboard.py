from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.ml.artifacts import MLArtifacts, get_artifacts
from app.models.customer import Customer
from app.schemas.dashboard import (
    ChurnDistribution,
    DashboardSummary,
    ModelCurve,
    ModelMetric,
    RiskDistribution,
    RocCurveResponse,
)
from app.security import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_summary(
    db: Session = Depends(get_db),
    artifacts: MLArtifacts = Depends(get_artifacts),
    _user: str = Depends(get_current_user),
):
    total = db.query(func.count(Customer.id)).scalar() or 0

    actual_churn_rate = db.query(func.avg(Customer.actual_churn)).scalar() or 0.0
    predicted_churn_rate = db.query(func.avg(Customer.churn_probability)).scalar() or 0.0

    def count_risk(level: str) -> int:
        return db.query(func.count(Customer.id)).filter(Customer.risk_level == level).scalar() or 0

    risk_distribution = RiskDistribution(
        high=count_risk("high"),
        medium=count_risk("medium"),
        low=count_risk("low"),
    )

    churned = db.query(func.count(Customer.id)).filter(Customer.actual_churn == 1).scalar() or 0
    non_churned = db.query(func.count(Customer.id)).filter(Customer.actual_churn == 0).scalar() or 0
    churn_distribution = ChurnDistribution(churn=churned, non_churn=non_churned)

    best = next(m for m in artifacts.models if m["name"] == artifacts.best_model_name)
    model_metrics = [
        ModelMetric(name=m["name"], f1=m["f1"], roc_auc=m["roc_auc"], accuracy=m["accuracy"])
        for m in artifacts.models
    ]

    return DashboardSummary(
        total_customers=total,
        actual_churn_rate=float(actual_churn_rate),
        predicted_churn_rate=float(predicted_churn_rate),
        best_model_accuracy=best["accuracy"],
        best_model_name=artifacts.best_model_name,
        risk_distribution=risk_distribution,
        churn_distribution=churn_distribution,
        model_metrics=model_metrics,
    )


@router.get("/roc-curve", response_model=RocCurveResponse)
def get_roc_curve(
    artifacts: MLArtifacts = Depends(get_artifacts), _user: str = Depends(get_current_user)
):
    """ROC curves of both models on the held-out test split, computed at training time."""
    return RocCurveResponse(
        curves=[
            ModelCurve(
                name=m["name"], fpr=m["fpr"], tpr=m["tpr"], auc=m["roc_auc"], accuracy=m["accuracy"]
            )
            for m in artifacts.models
        ]
    )
