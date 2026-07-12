import { apiRequest } from "../config/api";

export function fetchCustomers(query = "", includeInactive = false) {
  const params = new URLSearchParams();
  if (query) {
    params.set("q", query);
  }
  if (includeInactive) {
    params.set("include_inactive", "true");
  }
  const suffix = params.toString() ? `?${params.toString()}` : "";
  return apiRequest(`/sales-api/customers${suffix}`);
}

export function createCustomer(payload) {
  return apiRequest("/sales-api/customers", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateCustomer(customerId, payload) {
  return apiRequest(`/sales-api/customers/${customerId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function fetchNextSalesInvoice() {
  return apiRequest("/sales-api/invoices/next");
}

export function createSalesInvoice(payload) {
  return apiRequest("/sales-api/invoices", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function fetchSalesInvoices(filters = {}) {
  const params = new URLSearchParams();
  if (filters.q) params.set("q", filters.q);
  if (filters.start_date) params.set("start_date", filters.start_date);
  if (filters.end_date) params.set("end_date", filters.end_date);
  if (filters.status_filter) params.set("status_filter", filters.status_filter);
  const suffix = params.toString() ? `?${params.toString()}` : "";
  return apiRequest(`/sales-api/invoices${suffix}`);
}

export function fetchSalesInvoicePrint(invoiceId) {
  return apiRequest(`/sales-api/invoices/${invoiceId}/print`);
}

export function voidSalesInvoice(invoiceId, payload) {
  return apiRequest(`/sales-api/invoices/${invoiceId}/void`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function fetchCashCloseSummary(fecha, bodegaId = null) {
  const params = new URLSearchParams({ fecha });
  if (bodegaId) {
    params.set("bodega_id", String(bodegaId));
  }
  return apiRequest(`/sales-api/cash-close/summary?${params.toString()}`);
}

export function fetchCashClosures() {
  return apiRequest("/sales-api/cash-close");
}

export function createCashClose(payload) {
  return apiRequest("/sales-api/cash-close", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function fetchCashVouchers(startDate = "", endDate = "", bodegaId = null) {
  const params = new URLSearchParams();
  if (startDate) params.set("start_date", startDate);
  if (endDate) params.set("end_date", endDate);
  if (bodegaId) params.set("bodega_id", String(bodegaId));
  const suffix = params.toString() ? `?${params.toString()}` : "";
  return apiRequest(`/sales-api/cash-vouchers${suffix}`);
}

export function createCashVoucher(payload) {
  return apiRequest("/sales-api/cash-vouchers", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
