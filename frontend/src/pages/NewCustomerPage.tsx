import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import TextField from "@mui/material/TextField";
import MenuItem from "@mui/material/MenuItem";
import Grid from "@mui/material/Grid";
import Button from "@mui/material/Button";
import Alert from "@mui/material/Alert";
import CircularProgress from "@mui/material/CircularProgress";
import Divider from "@mui/material/Divider";
import PersonSearchIcon from "@mui/icons-material/PersonSearch";
import { createCustomer, getCustomerFieldOptions } from "../api/customers";
import { RiskBadge } from "../components/RiskBadge";
import { ReasonImpactChart } from "../components/ReasonImpactChart";
import type { CreateCustomerRequest, CustomerDetail, CustomerFieldOptions } from "../types";

type NumericKey = Exclude<keyof CreateCustomerRequest, "prefered_order_cat" | "marital_status">;

interface NumericField {
  key: NumericKey;
  label: string;
  min: number;
  max: number;
  step?: number;
  hint?: string;
}

const NUMERIC_FIELDS: NumericField[] = [
  { key: "tenure", label: "Tenure", min: 0, max: 100, hint: "months as a customer" },
  { key: "order_count", label: "Orders placed", min: 0, max: 500, hint: "last month" },
  { key: "day_since_last_order", label: "Days since last order", min: 0, max: 400 },
  { key: "cashback_amount", label: "Cashback earned", min: 0, max: 10000, step: 0.01 },
  { key: "satisfaction_score", label: "Satisfaction score", min: 1, max: 5, hint: "1 (worst) to 5" },
  { key: "number_of_address", label: "Saved addresses", min: 0, max: 50 },
  { key: "warehouse_to_home", label: "Warehouse to home", min: 0, max: 500, hint: "delivery distance" },
];

const EMPTY_FORM: Record<NumericKey, string> & { prefered_order_cat: string; marital_status: string; complain: string } = {
  tenure: "",
  order_count: "",
  day_since_last_order: "",
  cashback_amount: "",
  satisfaction_score: "",
  number_of_address: "",
  warehouse_to_home: "",
  complain: "0",
  prefered_order_cat: "",
  marital_status: "",
};

type FormState = typeof EMPTY_FORM;

export function NewCustomerPage() {
  const navigate = useNavigate();
  const [options, setOptions] = useState<CustomerFieldOptions | null>(null);
  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [showErrors, setShowErrors] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<CustomerDetail | null>(null);

  useEffect(() => {
    getCustomerFieldOptions().then(setOptions);
  }, []);

  function setField<K extends keyof FormState>(key: K, value: FormState[K]) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  function fieldError(f: NumericField): string | null {
    const raw = form[f.key];
    if (raw === "") return "Required";
    const n = Number(raw);
    if (Number.isNaN(n) || n < f.min || n > f.max) return `Enter ${f.min} to ${f.max}`;
    return null;
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setShowErrors(true);

    if (NUMERIC_FIELDS.some(fieldError) || !form.prefered_order_cat || !form.marital_status) {
      return;
    }

    const payload: CreateCustomerRequest = {
      tenure: Number(form.tenure),
      order_count: Number(form.order_count),
      day_since_last_order: Number(form.day_since_last_order),
      cashback_amount: Number(form.cashback_amount),
      satisfaction_score: Math.round(Number(form.satisfaction_score)),
      number_of_address: Math.round(Number(form.number_of_address)),
      warehouse_to_home: Number(form.warehouse_to_home),
      complain: Number(form.complain),
      prefered_order_cat: form.prefered_order_cat,
      marital_status: form.marital_status,
    };

    setSubmitting(true);
    try {
      setResult(await createCustomer(payload));
    } catch {
      setError("Could not run the prediction. Please check the values and try again.");
    } finally {
      setSubmitting(false);
    }
  }

  if (!options) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", mt: 8 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Predict Customer Churn
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Enter a few details to run the live churn model. The customer is saved to your records with
        the computed prediction.
      </Typography>

      <Grid container spacing={2}>
        <Grid size={{ xs: 12, md: 7 }}>
          <Card variant="outlined">
            <CardContent>
              <Box component="form" onSubmit={handleSubmit} noValidate>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  Activity
                </Typography>
                <Grid container spacing={2} sx={{ mb: 3 }}>
                  {NUMERIC_FIELDS.map((f) => {
                    const err = showErrors ? fieldError(f) : null;
                    return (
                      <Grid size={{ xs: 12, sm: 6 }} key={f.key}>
                        <TextField
                          label={f.label}
                          type="number"
                          fullWidth
                          size="small"
                          value={form[f.key]}
                          error={!!err}
                          helperText={err ?? f.hint ?? " "}
                          slotProps={{ htmlInput: { min: f.min, max: f.max, step: f.step ?? 1 } }}
                          onChange={(e) => setField(f.key, e.target.value)}
                        />
                      </Grid>
                    );
                  })}
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <TextField
                      select
                      label="Complaint filed?"
                      fullWidth
                      size="small"
                      value={form.complain}
                      helperText=" "
                      onChange={(e) => setField("complain", e.target.value)}
                    >
                      <MenuItem value="0">No</MenuItem>
                      <MenuItem value="1">Yes</MenuItem>
                    </TextField>
                  </Grid>
                </Grid>

                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  Profile
                </Typography>
                <Grid container spacing={2}>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <TextField
                      select
                      label="Preferred order category"
                      fullWidth
                      size="small"
                      value={form.prefered_order_cat}
                      error={showErrors && !form.prefered_order_cat}
                      helperText={showErrors && !form.prefered_order_cat ? "Required" : " "}
                      onChange={(e) => setField("prefered_order_cat", e.target.value)}
                    >
                      {options.prefered_order_cat.map((v) => (
                        <MenuItem key={v} value={v}>
                          {v}
                        </MenuItem>
                      ))}
                    </TextField>
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <TextField
                      select
                      label="Marital status"
                      fullWidth
                      size="small"
                      value={form.marital_status}
                      error={showErrors && !form.marital_status}
                      helperText={showErrors && !form.marital_status ? "Required" : " "}
                      onChange={(e) => setField("marital_status", e.target.value)}
                    >
                      {options.marital_status.map((v) => (
                        <MenuItem key={v} value={v}>
                          {v}
                        </MenuItem>
                      ))}
                    </TextField>
                  </Grid>
                </Grid>

                {error && (
                  <Alert severity="error" sx={{ mt: 1 }}>
                    {error}
                  </Alert>
                )}

                <Button
                  type="submit"
                  variant="contained"
                  sx={{ mt: 2 }}
                  disabled={submitting}
                  startIcon={submitting ? <CircularProgress size={16} color="inherit" /> : undefined}
                >
                  Predict churn
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, md: 5 }}>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="subtitle1" gutterBottom>
                Prediction results
              </Typography>

              {!result ? (
                <Box
                  sx={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    color: "text.secondary",
                    py: 4,
                  }}
                >
                  <PersonSearchIcon sx={{ fontSize: 40, mb: 1 }} />
                  <Typography variant="body2">
                    Fill in the form and click "Predict churn" to see results here.
                  </Typography>
                </Box>
              ) : (
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    Churn probability
                  </Typography>
                  <Typography
                    variant="h3"
                    color={result.risk_level === "high" ? "error" : result.risk_level === "medium" ? "warning" : "success"}
                  >
                    {(result.churn_probability * 100).toFixed(0)}%
                  </Typography>
                  <RiskBadge level={result.risk_level} />

                  <Typography variant="caption" color="text.secondary" sx={{ display: "block", mt: 1 }}>
                    Predicted live by the {result.model_name} model
                  </Typography>

                  <Divider sx={{ my: 2 }} />

                  <Typography variant="subtitle2" gutterBottom>
                    Top reasons
                  </Typography>
                  {result.reason_impacts.length > 0 ? (
                    <ReasonImpactChart reasons={result.reason_impacts} />
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      No risk factors to flag for this customer.
                    </Typography>
                  )}

                  <Button
                    size="small"
                    sx={{ mt: 2 }}
                    onClick={() => navigate(`/customers/${result.customer_id}`)}
                  >
                    View full customer record (#{result.customer_id})
                  </Button>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
