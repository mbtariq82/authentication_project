import { fetchWithAuth, getApiErrorMessage } from "./apiClient";
import type { Account } from "../types/account";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export async function getCurrentAccount(): Promise<Account> {
  const response = await fetchWithAuth(`${API_BASE_URL}/accounts/me`);

  if (!response.ok) {
    throw new Error(
      await getApiErrorMessage(response, "Failed to load your account."),
    );
  }

  return response.json() as Promise<Account>;
}

export async function freezeAccount(): Promise<Account> {
  const response = await fetchWithAuth(`${API_BASE_URL}/accounts/me/freeze`, {
    method: "PATCH",
  });

  if (!response.ok) {
    throw new Error(
      await getApiErrorMessage(response, "Failed to freeze your account."),
    );
  }

  return response.json() as Promise<Account>;
}

export async function unfreezeAccount(): Promise<Account> {
  const response = await fetchWithAuth(`${API_BASE_URL}/accounts/me/unfreeze`, {
    method: "PATCH",
  });

  if (!response.ok) {
    throw new Error(
      await getApiErrorMessage(response, "Failed to unfreeze your account."),
    );
  }

  return response.json() as Promise<Account>;
}

export async function closeAccount(closeReason: string): Promise<Account> {
  const response = await fetchWithAuth(`${API_BASE_URL}/accounts/me/close`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ close_reason: closeReason }),
  });

  if (!response.ok) {
    throw new Error(
      await getApiErrorMessage(response, "Failed to close your account."),
    );
  }

  return response.json() as Promise<Account>;
}
