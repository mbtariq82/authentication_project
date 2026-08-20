import { fetchWithAuth, type ApiErrorResponse } from "./apiClient";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export type LoanStatus = "PENDING" | "ACCEPTED" | "REJECTED" | "PAID";

export type Loan = {
  id: number;
  loan_type: string;
  loan_amount: number;
  duration: number;
  current_loan_status: LoanStatus;
  interest: number;
  emi: number;
};

export type LoanListResponse = {
  loans: Loan[];
};

export type LoanDecisionRequest = {
  status: "ACCEPTED" | "REJECTED";
};

export type LoanApplicationRequest = {
  loan_type: string;
  loan_amount: number;
  monthly_income: number;
  monthly_expenses: number;
  duration: number;
};

export type LoanApplicationResponse = {
  eligible: boolean;
  status: LoanStatus;
  loan_id: number | null;
};

export type LoanRepaymentRequest = {
  loan_id: number;
  amount: number;
};

export type LoanRepaymentResponse = {
  loan_id: number;
  repayment_amount: number;
  remaining_amount: number;
  status: LoanStatus;
};

export async function getUserLoans(): Promise<LoanListResponse> {
  const response = await fetchWithAuth(`${API_BASE_URL}/loans/my-loans`);

  if (!response.ok) {
    const errorData = (await response.json()) as ApiErrorResponse;

    throw new Error(errorData.detail ?? "Failed to load loans.");
  }

  return (await response.json()) as LoanListResponse;
}

export async function getPendingLoans(): Promise<LoanListResponse> {
  const response = await fetchWithAuth(`${API_BASE_URL}/loans/pending`);

  if (!response.ok) {
    const errorData = (await response.json()) as ApiErrorResponse;

    throw new Error(errorData.detail ?? "Failed to load pending loans.");
  }

  return (await response.json()) as LoanListResponse;
}

export async function updateLoanStatus(
  loanId: number,
  status: "ACCEPTED" | "REJECTED",
): Promise<LoanApplicationResponse> {
  const response = await fetchWithAuth(
    `${API_BASE_URL}/loans/${loanId}/decision`,
    {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        status,
      } satisfies LoanDecisionRequest),
    },
  );

  if (!response.ok) {
    const errorData = (await response.json()) as ApiErrorResponse;

    throw new Error(errorData.detail ?? "Failed to update loan status.");
  }

  return (await response.json()) as LoanApplicationResponse;
}

export async function repayLoan(
  request: LoanRepaymentRequest,
): Promise<LoanRepaymentResponse> {
  const response = await fetchWithAuth(`${API_BASE_URL}/loans/repay`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const errorData = (await response.json()) as ApiErrorResponse;

    throw new Error(errorData.detail ?? "Failed to make loan repayment.");
  }

  return (await response.json()) as LoanRepaymentResponse;
}

export async function applyForLoan(
  request: LoanApplicationRequest,
): Promise<LoanApplicationResponse> {
  const response = await fetchWithAuth(`${API_BASE_URL}/loans/loanForm`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const errorData = (await response.json()) as ApiErrorResponse;

    throw new Error(errorData.detail ?? "Failed to submit loan application.");
  }

  return (await response.json()) as LoanApplicationResponse;
}
