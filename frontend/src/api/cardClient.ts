import { fetchWithAuth, type ApiErrorResponse } from "./apiClient";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export type CardDetailsResponse = {
  card_number: string;
  expiry_date: string;
  cvc: string;
};

export type CardResponse = {
  id: number;
  account_id: number;
  card_number: string;
  expiry_date: string;
  cvc: string;
  status: string;
  created_at: string;
};

export type CardStatusResponse = {
  status: string;
};

export async function getUserCard(): Promise<CardDetailsResponse> {
  const response = await fetchWithAuth(`${API_BASE_URL}/cards`);

  if (!response.ok) {
    const errorData = (await response.json()) as ApiErrorResponse;

    throw new Error(errorData.detail ?? "Failed to load card.");
  }

  return response.json() as Promise<CardDetailsResponse>;
}

export async function getUnmaskedCard(
  password: string,
): Promise<CardDetailsResponse> {
  const response = await fetchWithAuth(`${API_BASE_URL}/cards/details`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      password,
    }),
  });

  if (!response.ok) {
    const errorData = (await response.json()) as ApiErrorResponse;

    throw new Error(errorData.detail ?? "Failed to retrieve card details.");
  }

  return response.json() as Promise<CardDetailsResponse>;
}

export async function createCard(): Promise<CardResponse> {
  const response = await fetchWithAuth(`${API_BASE_URL}/cards`, {
    method: "POST",
  });

  if (!response.ok) {
    const errorData = (await response.json()) as ApiErrorResponse;

    throw new Error(errorData.detail ?? "Failed to create card.");
  }

  return response.json() as Promise<CardResponse>;
}

export async function toggleCardStatus(): Promise<CardStatusResponse> {
  const response = await fetchWithAuth(`${API_BASE_URL}/cards/freeze`, {
    method: "PATCH",
  });

  if (!response.ok) {
    const errorData = (await response.json()) as ApiErrorResponse;

    throw new Error(errorData.detail ?? "Failed to update card status.");
  }

  return response.json() as Promise<CardStatusResponse>;
}
