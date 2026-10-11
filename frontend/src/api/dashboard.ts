import { apiClient } from "./client";
import type { DashboardSummary, LoginStats, RocCurveResponse } from "../types";

export async function getDashboardSummary(): Promise<DashboardSummary> {
  const { data } = await apiClient.get<DashboardSummary>("/api/dashboard/summary");
  return data;
}

export async function getRocCurve(): Promise<RocCurveResponse> {
  const { data } = await apiClient.get<RocCurveResponse>("/api/dashboard/roc-curve");
  return data;
}

export async function getLoginStats(): Promise<LoginStats> {
  const { data } = await apiClient.get<LoginStats>("/api/public/login-stats");
  return data;
}
