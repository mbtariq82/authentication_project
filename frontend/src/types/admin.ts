export type AccountStatus =
  | "pending"
  | "approved"
  | "reject"
  | "frozen"
  | "closed";
export type LoanStatus =
  | "pending"
  | "approved"
  | "rejected"
  | "cancelled"
  | "closed";
export type CardStatus = "active" | "frozen" | "expired" | "cancel";

export interface AdminAccount {
  id: number;
  customerName: string;
  customerEmail: string;
  accountNumber: string | null;
  accountType: "savings" | "current";
  status: AccountStatus;
  openedAt: string;
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
