import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import TablePagination from "@mui/material/TablePagination";
import Paper from "@mui/material/Paper";
import CircularProgress from "@mui/material/CircularProgress";
import Box from "@mui/material/Box";
import { useNavigate } from "react-router-dom";
import { RiskBadge } from "./RiskBadge";
import type { CustomerSummary } from "../types";

interface CustomerTableProps {
  rows: CustomerSummary[];
  total: number;
  page: number; // 0-indexed for MUI
  pageSize: number;
  loading: boolean;
  onPageChange: (page: number) => void;
  onPageSizeChange: (pageSize: number) => void;
}

export function CustomerTable({
  rows,
  total,
  page,
  pageSize,
  loading,
  onPageChange,
  onPageSizeChange,
}: CustomerTableProps) {
  const navigate = useNavigate();

  return (
    <Paper variant="outlined">
      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Customer ID</TableCell>
              <TableCell>Risk</TableCell>
              <TableCell align="right">Churn probability</TableCell>
              <TableCell align="right">Tenure (months)</TableCell>
              <TableCell>Order category</TableCell>
              <TableCell align="center">Complaint</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={6} align="center" sx={{ py: 4 }}>
                  <CircularProgress size={28} />
                </TableCell>
              </TableRow>
            ) : rows.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} align="center" sx={{ py: 4 }}>
                  No customers found.
                </TableCell>
              </TableRow>
            ) : (
              rows.map((row) => (
                <TableRow
                  key={row.customer_id}
                  hover
                  sx={{ cursor: "pointer" }}
                  onClick={() => navigate(`/customers/${row.customer_id}`)}
                >
                  <TableCell>{row.customer_id}</TableCell>
                  <TableCell>
                    <RiskBadge level={row.risk_level} />
                  </TableCell>
                  <TableCell align="right">{(row.churn_probability * 100).toFixed(1)}%</TableCell>
                  <TableCell align="right">{row.tenure ?? "-"}</TableCell>
                  <TableCell>{row.prefered_order_cat ?? "-"}</TableCell>
                  <TableCell align="center">{row.complain ? "Yes" : "No"}</TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
      <Box sx={{ display: "flex", justifyContent: "flex-end" }}>
        <TablePagination
          component="div"
          count={total}
          page={page}
          onPageChange={(_, newPage) => onPageChange(newPage)}
          rowsPerPage={pageSize}
          onRowsPerPageChange={(e) => onPageSizeChange(parseInt(e.target.value, 10))}
          rowsPerPageOptions={[10, 20, 50]}
        />
      </Box>
    </Paper>
  );
}
