"""One-time (idempotent) database seeding: reads the cleaned training data written by
mlpart/train.py, scores every customer with the trained model + SHAP explainer, and
writes it all into SQLite.

Run with: python -m app.seed [--reset]
"""

import argparse

import pandas as pd
from sqlalchemy.orm import Session

from app.database import Base, SessionLocal, engine
from app.ml.artifacts import get_artifacts
from app.ml.predict import predict_and_explain
from app.models.customer import Customer


def seed_database(db: Session, reset: bool = False) -> int:
    if reset:
        db.close()
        Base.metadata.drop_all(bind=engine, tables=[Customer.__table__])
    Base.metadata.create_all(bind=engine)

    if db.query(Customer).count() > 0:
        print("customers table already seeded, skipping (use --reset to force).")
        return db.query(Customer).count()

    artifacts = get_artifacts()
    df = pd.read_csv(artifacts.clean_csv_path)
    predictions = predict_and_explain(df, artifacts)

    for (_, row), pred in zip(df.iterrows(), predictions):
        db.add(
            Customer(
                customer_id=int(row["CustomerID"]),
                tenure=row["Tenure"],
                complain=int(row["Complain"]),
                day_since_last_order=row["DaySinceLastOrder"],
                cashback_amount=row["CashbackAmount"],
                satisfaction_score=int(row["SatisfactionScore"]),
                number_of_address=int(row["NumberOfAddress"]),
                order_count=row["OrderCount"],
                warehouse_to_home=row["WarehouseToHome"],
                prefered_order_cat=row["PreferedOrderCat"],
                marital_status=row["MaritalStatus"],
                actual_churn=int(row["Churn"]),
                **pred,
            )
        )

    db.commit()
    print(f"Seeding complete: {len(df)} customers.")
    return len(df)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="delete existing rows and reseed")
    args = parser.parse_args()

    session = SessionLocal()
    try:
        seed_database(session, reset=args.reset)
    finally:
        session.close()
