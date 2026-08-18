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
