from pydantic import BaseModel


class ModelMetric(BaseModel):
    name: str
    f1: float
    roc_auc: float
    accuracy: float


class RiskDistribution(BaseModel):
    high: int
    medium: int
    low: int


class ChurnDistribution(BaseModel):
    churn: int
    non_churn: int


class DashboardSummary(BaseModel):
    total_customers: int
    actual_churn_rate: float
    predicted_churn_rate: float
    best_model_accuracy: float
    best_model_name: str
    risk_distribution: RiskDistribution
    churn_distribution: ChurnDistribution
    model_metrics: list[ModelMetric]


class ModelCurve(BaseModel):
    name: str
    fpr: list[float]
    tpr: list[float]
    auc: float
    accuracy: float


class RocCurveResponse(BaseModel):
    curves: list[ModelCurve]
