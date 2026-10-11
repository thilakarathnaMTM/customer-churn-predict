from pydantic import BaseModel, Field


class CustomerSummary(BaseModel):
    customer_id: int
    churn_probability: float
    risk_level: str
    tenure: float | None
    prefered_order_cat: str | None
    complain: int | None

    class Config:
        from_attributes = True


class CustomerListResponse(BaseModel):
    items: list[CustomerSummary]
    total: int
    page: int
    page_size: int


class CustomerProfile(BaseModel):
    tenure: float | None
    complain: int | None
    day_since_last_order: float | None
    cashback_amount: float | None
    satisfaction_score: int | None
    number_of_address: int | None
    order_count: float | None
    warehouse_to_home: float | None
    prefered_order_cat: str | None
    marital_status: str | None

    class Config:
        from_attributes = True


class ReasonImpact(BaseModel):
    label: str
    impact_pct: float


class CustomerDetail(BaseModel):
    customer_id: int
    profile: CustomerProfile
    churn_probability: float
    risk_level: str
    top_reasons: list[str]
    reason_impacts: list[ReasonImpact]
    model_name: str  # the trained model that produced this prediction


class CreateCustomerRequest(BaseModel):
    tenure: float = Field(ge=0, le=100)
    complain: int = Field(ge=0, le=1)
    day_since_last_order: float = Field(ge=0, le=400)
    cashback_amount: float = Field(ge=0, le=10000)
    satisfaction_score: int = Field(ge=1, le=5)
    number_of_address: int = Field(ge=0, le=50)
    order_count: float = Field(ge=0, le=500)
    warehouse_to_home: float = Field(ge=0, le=500)
    prefered_order_cat: str
    marital_status: str


class CustomerFieldOptions(BaseModel):
    prefered_order_cat: list[str]
    marital_status: list[str]
