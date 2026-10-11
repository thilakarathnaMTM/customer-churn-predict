# customer-churn-predict

Predicts e-commerce customer churn from 10 simple inputs and explains each prediction.

## Model (`mlpart/`)

`python mlpart/train.py` cleans the data, tunes two models with 5-fold cross-validation
(XGBoost, Random Forest), evaluates once on a held-out 20% test split, and writes
`mlpart/artifacts/` (model, SHAP explainer, metrics, cleaned data).

- Merged duplicate category spellings (`Mobile` -> `Mobile Phone`).
- Dropped duplicate rows, which otherwise land in both train and test and inflate accuracy.
- Imputation and one-hot encoding live inside the model pipeline, fitted on training data only.
- Inputs: tenure, complaint, days since last order, cashback, satisfaction score, saved
  addresses, orders placed, delivery distance, order category, marital status.

Expect roughly 92% accuracy and 0.95 cross-validated ROC-AUC (0.96 on the test split).

## Run

```
cd backend
cp .env.example .env            # then set JWT_SECRET
pip install -r requirements.txt
python -m app.seed --reset
python -m app.seed_admin --username <user> --password <pass>
uvicorn app.main:app --reload

cd ../frontend
npm install && npm run dev
```
