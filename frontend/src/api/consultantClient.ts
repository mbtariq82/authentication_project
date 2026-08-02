import { type ApiErrorResponse } from "./apiClient";
import { fetchWithAuth } from "./apiClient";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

type ListConsultantsQuery = {
  page: number;
  page_size: number;
};

type Consultant = {
  id: number;
  user_id: number;
  email: string;
  first_name: string;
  last_name: string;
  batch: string;
  placement_status: string;
  client: string | null;
};

export type ConsultantPage = {
  items: Consultant[];
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
};

export async function getConsultants(
  query: ListConsultantsQuery,
): Promise<ConsultantPage> {
  const params = new URLSearchParams({
    page: query.page.toString(),
    page_size: query.page_size.toString(),
  });
  const response = await fetchWithAuth(
    `${API_BASE_URL}/admin/consultants?${params.toString()}`,
    {
      method: "GET",
    },
  );
  if (!response.ok) {
    const errorData = (await response.json()) as ApiErrorResponse;
    throw new Error(errorData.detail ?? "Failed to load consultants.");
  }
  return response.json() as Promise<ConsultantPage>;
}
