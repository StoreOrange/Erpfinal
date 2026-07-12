export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "";

// Funcion central para llamar al backend.
// Todas las pantallas usan esta ayuda para enviar el token, manejar errores
// y mantener las peticiones ordenadas en un solo lugar.
export async function apiRequest(path, options = {}) {
  const token = localStorage.getItem("token");
  const isFormData = options.body instanceof FormData;
  const headers = {
    ...(options.headers || {}),
  };

  if (!isFormData && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  const contentType = response.headers.get("content-type") || "";
  const payload = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const message =
      typeof payload === "object" && payload !== null
        ? payload.detail || payload.message || "Error en la solicitud"
        : payload || "Error en la solicitud";
    if (response.status === 404) {
      throw new Error(`Ruta no encontrada: ${API_BASE_URL}${path}`);
    }
    throw new Error(message);
  }

  return payload;
}
