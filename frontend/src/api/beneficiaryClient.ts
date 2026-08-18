import { fetchWithAuth, getApiErrorMessage } from "./apiClient";
import type {
  Beneficiary,
  CreateBeneficiaryRequest,
  UpdateBeneficiaryRequest,
} from "../types/beneficiary";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export async function getBeneficiaries(
  includeInactive = false,
): Promise<Beneficiary[]> {
  const params = new URLSearchParams({
    include_inactive: includeInactive.toString(),
  });
  const response = await fetchWithAuth(
    `${API_BASE_URL}/beneficiaries?${params.toString()}`,
  );
  if (!response.ok) {
    throw new Error(
      await getApiErrorMessage(response, "Failed to load beneficiaries."),
    );
  }
  return response.json() as Promise<Beneficiary[]>;
}

export async function getBeneficiary(
  beneficiaryId: number,
  includeInactive = false,
): Promise<Beneficiary> {
  const params = new URLSearchParams({
    include_inactive: includeInactive.toString(),
  });
  const response = await fetchWithAuth(
    `${API_BASE_URL}/beneficiaries/${beneficiaryId}?${params.toString()}`,
  );
  if (!response.ok) {
    throw new Error(
      await getApiErrorMessage(response, "Failed to load beneficiary."),
    );
  }
  return response.json() as Promise<Beneficiary>;
}

export async function createBeneficiary(
  request: CreateBeneficiaryRequest,
): Promise<Beneficiary> {
  const response = await fetchWithAuth(`${API_BASE_URL}/beneficiaries`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  if (!response.ok) {
    throw new Error(
      await getApiErrorMessage(response, "Failed to create beneficiary."),
    );
  }
  return response.json() as Promise<Beneficiary>;
}

export async function updateBeneficiary(
  beneficiaryId: number,
  request: UpdateBeneficiaryRequest,
): Promise<Beneficiary> {
  const response = await fetchWithAuth(
    `${API_BASE_URL}/beneficiaries/${beneficiaryId}`,
    {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
    },
  );
  if (!response.ok) {
    throw new Error(
      await getApiErrorMessage(response, "Failed to update beneficiary."),
    );
  }
  return response.json() as Promise<Beneficiary>;
}

export async function deactivateBeneficiary(
  beneficiaryId: number,
): Promise<Beneficiary> {
  const response = await fetchWithAuth(
    `${API_BASE_URL}/beneficiaries/${beneficiaryId}`,
    { method: "DELETE" },
  );
  if (!response.ok) {
    throw new Error(
      await getApiErrorMessage(response, "Failed to deactivate beneficiary."),
    );
  }
  return response.json() as Promise<Beneficiary>;
}
