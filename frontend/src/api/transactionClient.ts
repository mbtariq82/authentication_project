import { fetchWithAuth, getApiErrorMessage } from "./apiClient";
import type {
  CreateTransactionRequest,
  PaginatedResponse,
  Transaction,
  TransactionFilters,
  TransactionLog,
} from "../types/transaction";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

function buildQuery(filters: TransactionFilters): string {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(filters)) {
    if (value !== undefined && value !== "") {
      params.set(key, String(value));
    }
  }
  const query = params.toString();
  return query ? `?${query}` : "";
}

export async function createTransaction(
  request: CreateTransactionRequest,
): Promise<Transaction> {
  const response = await fetchWithAuth(`${API_BASE_URL}/transactions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  if (!response.ok) {
    throw new Error(
      await getApiErrorMessage(response, "Failed to create transaction."),
    );
  }
  return response.json() as Promise<Transaction>;
}

export async function getTransactions(
  filters: TransactionFilters = {},
): Promise<PaginatedResponse<Transaction>> {
  const response = await fetchWithAuth(
    `${API_BASE_URL}/transactions${buildQuery(filters)}`,
  );
  if (!response.ok) {
    throw new Error(
      await getApiErrorMessage(response, "Failed to load transactions."),
    );
  }
  return response.json() as Promise<PaginatedResponse<Transaction>>;
}

export async function getTransaction(
  transactionId: number,
): Promise<Transaction> {
  const response = await fetchWithAuth(
    `${API_BASE_URL}/transactions/${transactionId}`,
  );
  if (!response.ok) {
    throw new Error(
      await getApiErrorMessage(response, "Failed to load transaction."),
    );
  }
  return response.json() as Promise<Transaction>;
}

export async function cancelTransaction(
  transactionId: number,
): Promise<Transaction> {
  const response = await fetchWithAuth(
    `${API_BASE_URL}/transactions/${transactionId}/cancel`,
    { method: "POST" },
  );
  if (!response.ok) {
    throw new Error(
      await getApiErrorMessage(response, "Failed to cancel transaction."),
    );
  }
  return response.json() as Promise<Transaction>;
}

export async function getTransactionLogs(
  transactionId: number,
): Promise<TransactionLog[]> {
  const response = await fetchWithAuth(
    `${API_BASE_URL}/transactions/${transactionId}/logs`,
  );
  if (!response.ok) {
    throw new Error(
      await getApiErrorMessage(response, "Failed to load transaction logs."),
    );
  }
  return response.json() as Promise<TransactionLog[]>;
}
