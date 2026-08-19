import type {
  AdminAccount,
  AdminLoan,
  AdminCard,
  AccountStatus,
  LoanStatus,
  CardStatus,
  AdminUser,
  UserStatus,
} from "../types/admin";

import { fetchWithAuth, type ApiErrorResponse } from "./apiClient";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

async function handle<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorData = (await response
      .json()
      .catch(() => ({}))) as ApiErrorResponse;

    throw new Error(
      errorData.detail ?? `Request failed with status ${response.status}`,
    );
  }

  return response.json() as Promise<T>;
}

// ---------------- USERS ----------------
export async function fetchUsers(skip = 0, limit = 100): Promise<AdminUser[]> {
  const response = await fetchWithAuth(
    `${API_BASE_URL}/admin/all_users?skip=${skip}&limit=${limit}`,
  );

  if (!response.ok) {
    const data = await response.json().catch(() => ({}));

    throw new Error(data.detail ?? `Failed to load users: ${response.status}`);
  }

  return response.json() as Promise<AdminUser[]>;
}

export async function updateUserStatus(
  userId: number,
  status: UserStatus,
  rejectionReason?: string,
): Promise<AdminUser> {
  const response = await fetchWithAuth(`${API_BASE_URL}/admin/users/status`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      user_id: userId,
      status: status,
      rejection_reason: rejectionReason ?? null,
    }),
  });

  return handle<AdminUser>(response);
}

// ---------------- ACCOUNTS ----------------

export async function fetchAccounts(
  skip = 0,
  limit = 100,
): Promise<AdminAccount[]> {
  const response = await fetchWithAuth(
    `${API_BASE_URL}/admin/all_accounts?skip=${skip}&limit=${limit}`,
    {
      method: "GET",
    },
  );

  return handle<AdminAccount[]>(response);
}

export async function updateAccountStatus(
  accountId: number,
  status: AccountStatus,
): Promise<AdminAccount> {
  const response = await fetchWithAuth(
    `${API_BASE_URL}/admin/accounts/${accountId}/status`,
    {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        status,
      }),
    },
  );

  return handle<AdminAccount>(response);
}

// ---------------- LOANS ----------------

export async function fetchLoans(skip = 0, limit = 100): Promise<AdminLoan[]> {
  const response = await fetchWithAuth(
    `${API_BASE_URL}/admin/all_loans?skip=${skip}&limit=${limit}`,
    {
      method: "GET",
    },
  );

  return handle<AdminLoan[]>(response);
}

export async function updateLoanStatus(
  loanId: number,
  status: LoanStatus,
): Promise<AdminLoan> {
  const response = await fetchWithAuth(
    `${API_BASE_URL}/admin/loans/${loanId}/status`,
    {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        status,
      }),
    },
  );

  return handle<AdminLoan>(response);
}

// ---------------- CARDS ----------------

export async function fetchCards(skip = 0, limit = 100): Promise<AdminCard[]> {
  const response = await fetchWithAuth(
    `${API_BASE_URL}/admin/all_cards?skip=${skip}&limit=${limit}`,
    {
      method: "GET",
    },
  );

  return handle<AdminCard[]>(response);
}

export async function updateCardStatus(
  cardId: number,
  status: CardStatus,
): Promise<AdminCard> {
  const response = await fetchWithAuth(
    `${API_BASE_URL}/admin/cards/${cardId}/status`,
    {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        status,
      }),
    },
  );

  return handle<AdminCard>(response);
}
