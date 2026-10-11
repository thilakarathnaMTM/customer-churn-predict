from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, Integer, JSON, String

from app.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, unique=True, index=True, nullable=False)

    # model inputs (see mlpart/train.py)
    tenure = Column(Float)
    complain = Column(Integer)
    day_since_last_order = Column(Float)
    cashback_amount = Column(Float)
    satisfaction_score = Column(Integer)
    number_of_address = Column(Integer)
    order_count = Column(Float)
    warehouse_to_home = Column(Float)
    prefered_order_cat = Column(String)
    marital_status = Column(String)

    actual_churn = Column(Integer)  # ground-truth label from the training CSV; null for new customers

    churn_probability = Column(Float, index=True)
    risk_level = Column(String, index=True)
    top_reasons = Column(JSON)
    reason_impacts = Column(JSON)  # [{"label": str, "impact_pct": float}, ...]
    predicted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
