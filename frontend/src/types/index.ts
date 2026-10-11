export type RiskLevel = "high" | "medium" | "low";

export interface ModelMetric {
  name: string;
  f1: number;
  roc_auc: number;
  accuracy: number;
}

export interface RiskDistribution {
  high: number;
  medium: number;
  low: number;
}

export interface ChurnDistribution {
  churn: number;
  non_churn: number;
}

export interface DashboardSummary {
  total_customers: number;
  actual_churn_rate: number;
  predicted_churn_rate: number;
  best_model_accuracy: number;
  best_model_name: string;
  risk_distribution: RiskDistribution;
  churn_distribution: ChurnDistribution;
  model_metrics: ModelMetric[];
}

export interface ModelCurve {
  name: string;
  fpr: number[];
  tpr: number[];
  auc: number;
  accuracy: number;
}

export interface RocCurveResponse {
  curves: ModelCurve[];
}

export interface CustomerSummary {
  customer_id: number;
  churn_probability: number;
  risk_level: RiskLevel;
  tenure: number | null;
  prefered_order_cat: string | null;
  complain: number | null;
}

export interface CustomerListResponse {
  items: CustomerSummary[];
  total: number;
  page: number;
  page_size: number;
}

export interface CustomerProfile {
  tenure: number | null;
  complain: number | null;
  day_since_last_order: number | null;
  cashback_amount: number | null;
  satisfaction_score: number | null;
  number_of_address: number | null;
  order_count: number | null;
  warehouse_to_home: number | null;
  prefered_order_cat: string | null;
  marital_status: string | null;
}

export interface ReasonImpact {
  label: string;
  impact_pct: number;
}

export interface CustomerDetail {
  customer_id: number;
  profile: CustomerProfile;
  churn_probability: number;
  risk_level: RiskLevel;
  top_reasons: string[];
  reason_impacts: ReasonImpact[];
  model_name: string;
}

export interface CustomerFieldOptions {
  prefered_order_cat: string[];
  marital_status: string[];
}

export interface CreateCustomerRequest {
  tenure: number;
  complain: number;
  day_since_last_order: number;
  cashback_amount: number;
  satisfaction_score: number;
  number_of_address: number;
  order_count: number;
  warehouse_to_home: number;
  prefered_order_cat: string;
  marital_status: string;
}

export interface RiskExample {
  customer_id: number;
  churn_probability: number;
  risk_level: RiskLevel;
}

export interface LoginStats {
  total_customers: number;
  best_model_auc: number;
  risk_examples: RiskExample[];
  last_scored_at: string | null;
}
