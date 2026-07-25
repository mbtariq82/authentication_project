import { fetchWithAuth, type ApiErrorResponse } from "./apiClient";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export type AdminDashboardResponse = {
  id: number;
  email: string;
  role: "ADMIN";
  // totalConsultants: number;
  // placedConsultants: number;
  // availableConsultants: number;
  // endingSoon: number;
};

export async function getAdminDashboard(): Promise<AdminDashboardResponse> {
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

  return response.json() as Promise<AdminDashboardResponse>;
}