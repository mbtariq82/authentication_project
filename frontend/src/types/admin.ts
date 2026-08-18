export type LoanStatus =
  | "pending"
  | "approved"
  | "rejected"
  | "cancelled"
  | "closed";
export type CardStatus = "active" | "frozen" | "expired" | "cancel";

export type AccountStatus =
  | "pending"
  | "approved"
  | "rejected"
  | "frozen"
  | "closed";

export interface AdminAccount {
  id: number;
  account_number: string | null;
  account_type: string;
  account_status: AccountStatus;
  created_at: string;

  first_name?: string;
  last_name?: string;
  email?: string;
}

export interface AdminLoan {
  id: number;
  customerName: string;
  customerEmail: string;
  loanType: string;
  amount: number;
  durationMonths: number;
  status: LoanStatus;
  appliedAt: string;
}

export interface AdminCard {
  id: number;
  customerName: string;
  customerEmail: string;
  cardType: "debit" | "credit";
  cardNumberMasked: string;
  status: CardStatus;
  issuedAt: string;
}

export type PanelKey = "accounts" | "loans" | "cards";
