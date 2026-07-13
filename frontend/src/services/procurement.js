import { apiRequest } from "../config/api";

function queryString(params = {}) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== "") {
      query.set(key, String(value));
    }
  });
  const text = query.toString();
  return text ? `?${text}` : "";
}

export function fetchProcurementSummary() {
  return apiRequest("/procurement/summary");
}

export function fetchSupplyCatalogs(params = {}) {
  return apiRequest(`/procurement/catalogs${queryString(params)}`);
}

export function createSupplyCategory(payload) {
  return apiRequest("/procurement/catalogs/categories", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateSupplyCategory(categoryId, payload) {
  return apiRequest(`/procurement/catalogs/categories/${categoryId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function createSupplyUnit(payload) {
  return apiRequest("/procurement/catalogs/units", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateSupplyUnit(unitId, payload) {
  return apiRequest(`/procurement/catalogs/units/${unitId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function fetchSupplies(params = {}) {
  return apiRequest(`/procurement/supplies${queryString(params)}`);
}

export function createSupply(payload) {
  return apiRequest("/procurement/supplies", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateSupply(itemId, payload) {
  return apiRequest(`/procurement/supplies/${itemId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function fetchSupplyMovements(params = {}) {
  return apiRequest(`/procurement/movements${queryString(params)}`);
}

export function createSupplyMovement(payload) {
  return apiRequest("/procurement/movements", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function fetchQuoteRequests(params = {}) {
  return apiRequest(`/procurement/quote-requests${queryString(params)}`);
}

export function createQuoteRequest(payload) {
  return apiRequest("/procurement/quote-requests", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateQuoteRequest(requestId, payload) {
  return apiRequest(`/procurement/quote-requests/${requestId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function addSupplierQuote(requestId, payload) {
  return apiRequest(`/procurement/quote-requests/${requestId}/quotes`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function fetchEmailConfig() {
  return apiRequest("/procurement/notifications/config");
}

export function saveEmailConfig(payload) {
  return apiRequest("/procurement/notifications/config", {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function fetchNotificationRecipients() {
  return apiRequest("/procurement/notifications/recipients");
}

export function createNotificationRecipient(payload) {
  return apiRequest("/procurement/notifications/recipients", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateNotificationRecipient(recipientId, payload) {
  return apiRequest(`/procurement/notifications/recipients/${recipientId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function sendQuoteRequestEmail(requestId) {
  return apiRequest(`/procurement/quote-requests/${requestId}/send-email`, {
    method: "POST",
  });
}
