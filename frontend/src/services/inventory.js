import { apiRequest } from "../config/api";

export function fetchInventoryCatalogs() {
  return apiRequest("/inventory/catalogs");
}

export function fetchProducts(query = "", includeInactive = false) {
  const params = new URLSearchParams();
  if (query) {
    params.set("q", query);
  }
  if (includeInactive) {
    params.set("include_inactive", "true");
  }
  const suffix = params.toString() ? `?${params.toString()}` : "";
  return apiRequest(`/inventory/products${suffix}`);
}

export function fetchNextProductCode() {
  return apiRequest("/inventory/products/next-code");
}

export function createProduct(payload) {
  return apiRequest("/inventory/products", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateProduct(productId, payload) {
  return apiRequest(`/inventory/products/${productId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function toggleProductActive(productId) {
  return apiRequest(`/inventory/products/${productId}/toggle-active`, {
    method: "PATCH",
  });
}

export function fetchProductRecipe(productId) {
  return apiRequest(`/inventory/products/${productId}/recipe`);
}

export function saveProductRecipe(productId, payload) {
  return apiRequest(`/inventory/products/${productId}/recipe`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function fetchProductCombo(productId) {
  return apiRequest(`/inventory/products/${productId}/combo`);
}

export function saveProductComboItem(productId, payload) {
  return apiRequest(`/inventory/products/${productId}/combo`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function deleteProductComboItem(productId, comboId) {
  return apiRequest(`/inventory/products/${productId}/combo/${comboId}`, {
    method: "DELETE",
  });
}

export function createMarca(payload) {
  return apiRequest("/inventory/marcas", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function createProveedor(payload) {
  return apiRequest("/inventory/proveedores", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateProveedor(proveedorId, payload) {
  return apiRequest(`/inventory/proveedores/${proveedorId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function createBodega(payload) {
  return apiRequest("/inventory/bodegas", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateBodega(bodegaId, payload) {
  return apiRequest(`/inventory/bodegas/${bodegaId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function createLinea(payload) {
  return apiRequest("/inventory/lineas", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateLinea(lineaId, payload) {
  return apiRequest(`/inventory/lineas/${lineaId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function createSegmento(payload) {
  return apiRequest("/inventory/segmentos", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateSegmento(segmentoId, payload) {
  return apiRequest(`/inventory/segmentos/${segmentoId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function createUnidadMedida(payload) {
  return apiRequest("/inventory/unidades-medida", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateUnidadMedida(unidadId, payload) {
  return apiRequest(`/inventory/unidades-medida/${unidadId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function updateMarca(marcaId, payload) {
  return apiRequest(`/inventory/marcas/${marcaId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function fetchIngresos() {
  return apiRequest("/inventory/ingresos");
}

export function fetchEgresos() {
  return apiRequest("/inventory/egresos");
}

export function createIngreso(payload) {
  return apiRequest("/inventory/ingresos", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function createEgreso(payload) {
  return apiRequest("/inventory/egresos", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function fetchProductions() {
  return apiRequest("/inventory/producciones");
}

export function openProduction(payload) {
  return apiRequest("/inventory/producciones/open", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function executeProduction(productionId) {
  return apiRequest(`/inventory/producciones/${productionId}/execute`, {
    method: "POST",
  });
}

export function fetchProductionReport(productionId) {
  return apiRequest(`/inventory/producciones/${productionId}/report`);
}

export function fetchPacaOpenings() {
  return apiRequest("/inventory/paca-aperturas");
}

export function createPacaOpening(payload) {
  return apiRequest("/inventory/paca-aperturas", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function fetchPacaOpeningReport(openingId) {
  return apiRequest(`/inventory/paca-aperturas/${openingId}/report`);
}

export function fetchProductBalances(productId) {
  return apiRequest(`/inventory/products/${productId}/balances`);
}

export function searchInventoryProducts(query, bodegaId = null, priceList = 1) {
  const params = new URLSearchParams();
  params.set("q", query);
  params.set("price_list", String(priceList));
  if (bodegaId) {
    params.set("bodega_id", String(bodegaId));
  }
  return apiRequest(`/inventory/products/search?${params.toString()}`);
}
