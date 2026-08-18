import type {
  AdminAccount,
  AdminLoan,
  AdminCard,
  AccountStatus,
  LoanStatus,
  CardStatus,
} from "../types/admin";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/admin";

function authHeaders(): HeadersInit {
  const token = localStorage.getItem("admin_token") ?? "";
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };
}

async function handle<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail ?? `Request failed with status ${res.status}`);
  }
  return res.json() as Promise<T>;
}

// ---------- Accounts ----------
export async function fetchAccounts(
  status?: AccountStatus,
): Promise<AdminAccount[]> {
  const url = status
    ? `${BASE_URL}/accounts?status=${status}`
    : `${BASE_URL}/accounts`;
  const res = await fetch(url, { headers: authHeaders() });
  return handle<AdminAccount[]>(res);
}

export async function updateAccountStatus(
  accountId: number,
  status: AccountStatus,
  reason?: string,
): Promise<AdminAccount> {
  const res = await fetch(`${BASE_URL}/accounts/${accountId}/status`, {
    method: "PATCH",
    headers: authHeaders(),
    body: JSON.stringify({ status, reason }),
  });
  return handle<AdminAccount>(res);
}

// ---------- Loans ----------
// NOTE: these endpoints don't exist in the backend yet — add matching
// FastAPI routes (PATCH /admin/loans/{id}/status) when loan approval
// is wired up server-side. Shaped to mirror the accounts pattern.
export async function fetchLoans(status?: LoanStatus): Promise<AdminLoan[]> {
  const url = status
    ? `${BASE_URL}/loans?status=${status}`
    : `${BASE_URL}/loans`;
  const res = await fetch(url, { headers: authHeaders() });
  return handle<AdminLoan[]>(res);
}

export async function updateLoanStatus(
  loanId: number,
  status: LoanStatus,
  reason?: string,
): Promise<AdminLoan> {
  const res = await fetch(`${BASE_URL}/loans/${loanId}/status`, {
    method: "PATCH",
    headers: authHeaders(),
    body: JSON.stringify({ status, reason }),
  });
  return handle<AdminLoan>(res);
}

// ---------- Cards ----------
// NOTE: same as loans above — backend routes not implemented yet.
export async function fetchCards(status?: CardStatus): Promise<AdminCard[]> {
  const url = status
    ? `${BASE_URL}/cards?status=${status}`
    : `${BASE_URL}/cards`;
  const res = await fetch(url, { headers: authHeaders() });
  return handle<AdminCard[]>(res);
}

export async function updateCardStatus(
  cardId: number,
  status: CardStatus,
): Promise<AdminCard> {
  const res = await fetch(`${BASE_URL}/cards/${cardId}/status`, {
    method: "PATCH",
    headers: authHeaders(),
    body: JSON.stringify({ status }),
  });
  return handle<AdminCard>(res);
}
