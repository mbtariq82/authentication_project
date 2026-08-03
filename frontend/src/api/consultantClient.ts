import { type ApiErrorResponse } from "./apiClient";
import { fetchWithAuth } from "./apiClient";
import type {
  Consultant,
  CreateConsultantRequest,
  UnassignedUser,
} from "../types/consultant";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

type ListConsultantsQuery = {
  page: number;
  page_size: number;
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

export async function getUnassignedUsers(): Promise<UnassignedUser[]> {
  const response = await fetchWithAuth(`${API_BASE_URL}/admin/users`, {
    method: "GET",
  });
  if (!response.ok) {
    const errorData = (await response.json()) as ApiErrorResponse;
    throw new Error(errorData.detail ?? "Failed to load unassigned users.");
  }
  return response.json() as Promise<UnassignedUser[]>;
}

export async function createConsultant(
  request: CreateConsultantRequest,
): Promise<Consultant> {
  const response = await fetchWithAuth(`${API_BASE_URL}/admin/consultants/new`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });
  if (!response.ok) {
    const errorData = (await response.json()) as ApiErrorResponse;
    throw new Error(errorData.detail ?? "Failed to create consultant.");
  }
  return response.json() as Promise<Consultant>;
}
