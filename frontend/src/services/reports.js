import { apiRequest } from "../config/api";

function buildQuery(filters = {}) {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== "") {
      params.set(key, String(value));
    }
  });
  const query = params.toString();
  return query ? `?${query}` : "";
}

export function fetchReportCatalogs() {
  return apiRequest("/reports/catalogs");
}

export function fetchReportsSummary(filters) {
  return apiRequest(`/reports/summary${buildQuery(filters)}`);
}

export function fetchSalesDashboardReport(filters) {
  return apiRequest(`/reports/sales-dashboard${buildQuery(filters)}`);
}

export function fetchSalesDetailedReport(filters) {
  return apiRequest(`/reports/sales-detailed${buildQuery(filters)}`);
}

export function fetchSalesProductsReport(filters) {
  return apiRequest(`/reports/sales-products${buildQuery(filters)}`);
}

export function fetchProfitReport(filters) {
  return apiRequest(`/reports/profit${buildQuery(filters)}`);
}

export function fetchInventoryConsolidatedReport() {
  return apiRequest("/reports/inventory-consolidated");
}

export function fetchWarehouseBalancesReport(filters) {
  return apiRequest(`/reports/saldos-bodega${buildQuery(filters)}`);
}

export function fetchInventoryExistencesReport(filters) {
  return apiRequest(`/reports/inventory-existences${buildQuery(filters)}`);
}

export function fetchKardexReport(filters) {
  return apiRequest(`/reports/kardex${buildQuery(filters)}`);
}

export function fetchCashVouchersReport(filters) {
  return apiRequest(`/reports/cash-vouchers${buildQuery(filters)}`);
}

export function fetchStagnantProductsReport(filters) {
  return apiRequest(`/reports/stagnant-products${buildQuery(filters)}`);
}

export function fetchTopMovementReport(filters) {
  return apiRequest(`/reports/top-movement${buildQuery(filters)}`);
}

export function fetchLowStockReport(filters) {
  return apiRequest(`/reports/low-stock${buildQuery(filters)}`);
}

export function fetchNoStockReport() {
  return apiRequest("/reports/no-stock");
}
