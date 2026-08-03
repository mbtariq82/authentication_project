import { fetchWithAuth, type ApiErrorResponse } from "./apiClient";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export async function getAdminDashboard() {
  const response = await fetchWithAuth(
    `${API_BASE_URL}/admin/dashboard`,
  );
  if (!response.ok) {
    const errorData =
      (await response.json()) as ApiErrorResponse;
    throw new Error(
      errorData.detail ?? "Failed to load admin dashboard.",
    );
  }
  return response.json();
}