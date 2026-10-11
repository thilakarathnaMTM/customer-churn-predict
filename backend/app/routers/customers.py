import logging

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.ml.artifacts import MLArtifacts, get_artifacts
from app.ml.predict import predict_and_explain
from app.models.customer import Customer
from app.schemas.customer import (
    CreateCustomerRequest,
    CustomerDetail,
    CustomerFieldOptions,
    CustomerListResponse,
    CustomerProfile,
    CustomerSummary,
)
from app.security import get_current_user

logger = logging.getLogger("uvicorn.error")

router = APIRouter(prefix="/api/customers", tags=["customers"])


@router.get("", response_model=CustomerListResponse)
def list_customers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    search: str | None = None,
    risk_level: str | None = Query(None, pattern="^(high|medium|low)$"),
    prefered_order_cat: str | None = None,
    sort_dir: str = Query("desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    q = db.query(Customer)

    if risk_level:
        q = q.filter(Customer.risk_level == risk_level)

    if prefered_order_cat:
        q = q.filter(Customer.prefered_order_cat == prefered_order_cat)

    if search:
        search = search.strip()
        if search.isdigit():
            q = q.filter(Customer.customer_id == int(search))
        else:
            q = q.filter(Customer.prefered_order_cat.ilike(f"%{search}%"))

    total = q.count()

    order_col = Customer.churn_probability
    q = q.order_by(order_col.desc() if sort_dir == "desc" else order_col.asc())

    rows = q.offset((page - 1) * page_size).limit(page_size).all()

    return CustomerListResponse(
        items=[CustomerSummary.model_validate(r) for r in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/meta/options", response_model=CustomerFieldOptions)
def get_field_options(
    artifacts: MLArtifacts = Depends(get_artifacts), _user: str = Depends(get_current_user)
):
    """Allowed values for each categorical input, taken from the cleaned training data —
    the form must only submit values from these lists."""
    opts = artifacts.category_options
    return CustomerFieldOptions(
        prefered_order_cat=opts["PreferedOrderCat"], marital_status=opts["MaritalStatus"]
    )


def _get_customer_or_404(db: Session, customer_id: int) -> Customer:
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


def _to_detail(customer: Customer, artifacts: MLArtifacts) -> CustomerDetail:
    return CustomerDetail(
        customer_id=customer.customer_id,
        profile=CustomerProfile.model_validate(customer),
        churn_probability=customer.churn_probability,
        risk_level=customer.risk_level,
        top_reasons=customer.top_reasons or [],
        reason_impacts=customer.reason_impacts or [],
        model_name=artifacts.best_model_name,
    )


@router.get("/{customer_id}", response_model=CustomerDetail)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    artifacts: MLArtifacts = Depends(get_artifacts),
    _user: str = Depends(get_current_user),
):
    return _to_detail(_get_customer_or_404(db, customer_id), artifacts)


@router.post("", response_model=CustomerDetail, status_code=201)
def create_customer(
    payload: CreateCustomerRequest,
    db: Session = Depends(get_db),
    artifacts: MLArtifacts = Depends(get_artifacts),
    _user: str = Depends(get_current_user),
):
    """Adds a new customer, runs the churn model + SHAP on them immediately, and stores the result."""
    opts = artifacts.category_options
    if payload.prefered_order_cat not in opts["PreferedOrderCat"]:
        raise HTTPException(status_code=422, detail="Unknown order category")
    if payload.marital_status not in opts["MaritalStatus"]:
        raise HTTPException(status_code=422, detail="Unknown marital status")

    next_id = (db.query(func.max(Customer.customer_id)).scalar() or 59999) + 1

    raw_row = pd.DataFrame(
        [
            {
                "Tenure": payload.tenure,
                "Complain": payload.complain,
                "DaySinceLastOrder": payload.day_since_last_order,
                "CashbackAmount": payload.cashback_amount,
                "SatisfactionScore": payload.satisfaction_score,
                "NumberOfAddress": payload.number_of_address,
                "OrderCount": payload.order_count,
                "WarehouseToHome": payload.warehouse_to_home,
                "PreferedOrderCat": payload.prefered_order_cat,
                "MaritalStatus": payload.marital_status,
            }
        ]
    )
    pred = predict_and_explain(raw_row, artifacts)[0]

    customer = Customer(customer_id=next_id, **payload.model_dump(), **pred)
    db.add(customer)
    db.commit()
    logger.info(
        "[%s] Predicted customer %s: %.1f%% churn (%s risk), reasons=%s",
        artifacts.best_model_name, next_id, pred["churn_probability"] * 100, pred["risk_level"], pred["top_reasons"],
    )

    return _to_detail(customer, artifacts)
