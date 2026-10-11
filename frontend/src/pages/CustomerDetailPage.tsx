import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import Stack from "@mui/material/Stack";
import CircularProgress from "@mui/material/CircularProgress";
import Button from "@mui/material/Button";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import { getCustomerDetail } from "../api/customers";
import { RiskBadge } from "../components/RiskBadge";
import { ReasonImpactChart } from "../components/ReasonImpactChart";
import type { CustomerDetail } from "../types";

export function CustomerDetailPage() {
  const { customerId } = useParams<{ customerId: string }>();
  const navigate = useNavigate();
  const [detail, setDetail] = useState<CustomerDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!customerId) return;
    setLoading(true);
    getCustomerDetail(Number(customerId))
      .then(setDetail)
      .finally(() => setLoading(false));
  }, [customerId]);

  if (loading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", mt: 8 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!detail) {
    return <Typography color="error">Customer not found.</Typography>;
  }

  const p = detail.profile;

  return (
    <Box>
      <Button startIcon={<ArrowBackIcon />} onClick={() => navigate(-1)} sx={{ mb: 2 }}>
        Back
      </Button>

      <Stack direction="row" spacing={2} sx={{ alignItems: "center", mb: 3 }}>
        <Typography variant="h5">Customer #{detail.customer_id}</Typography>
        <RiskBadge level={detail.risk_level} />
        <Chip label={`${(detail.churn_probability * 100).toFixed(1)}% churn probability`} />
        <Chip variant="outlined" label={`Model: ${detail.model_name}`} />
      </Stack>

      <Grid container spacing={2}>
        <Grid size={{ xs: 12, md: 6 }}>
          <Card variant="outlined" sx={{ height: "100%" }}>
            <CardContent>
              <Typography variant="subtitle1" gutterBottom>
                Main risk factors
              </Typography>
              {detail.reason_impacts.length === 0 ? (
                <Typography variant="body2" color="text.secondary">
                  No risk factors to flag for this customer.
                </Typography>
              ) : (
                <ReasonImpactChart reasons={detail.reason_impacts} />
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, md: 6 }}>
          <Card variant="outlined" sx={{ height: "100%" }}>
            <CardContent>
              <Typography variant="subtitle1" gutterBottom>
                Profile
              </Typography>
              <Grid container spacing={1.5}>
                <ProfileField label="Tenure (months)" value={p.tenure} />
                <ProfileField label="Order count" value={p.order_count} />
                <ProfileField label="Days since last order" value={p.day_since_last_order} />
                <ProfileField label="Complaint filed" value={p.complain ? "Yes" : "No"} />
                <ProfileField label="Satisfaction score" value={p.satisfaction_score} />
                <ProfileField label="Cashback amount" value={p.cashback_amount} />
                <ProfileField label="Saved addresses" value={p.number_of_address} />
                <ProfileField label="Warehouse to home distance" value={p.warehouse_to_home} />
                <ProfileField label="Preferred order category" value={p.prefered_order_cat} />
                <ProfileField label="Marital status" value={p.marital_status} />
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

function ProfileField({ label, value }: { label: string; value: string | number | null | undefined }) {
  return (
    <Grid size={6}>
      <Typography variant="caption" color="text.secondary" sx={{ display: "block" }}>
        {label}
      </Typography>
      <Typography variant="body2">{value ?? "-"}</Typography>
    </Grid>
  );
}
