export type LoanStatus = "PENDING" | "ACCEPTED" | "REJECTED";
export type AccountStatus =
  | "PENDING"
  | "APPROVED"
  | "FROZEN"
  | "CLOSED"
  | "REJECTED";

export interface AdminAccount {
  id: number;
  user_id: number;

  account_number: string | null;
  sort_code?: string | null;
  branch?: string | null;
  account_type: string;
  balance?: string | number;

  account_status: AccountStatus;

  first_name?: string;
  last_name?: string;
  email?: string;

  close_reason?: string | null;
  closed_at?: string | null;

  created_at: string;
  updated_at?: string;
}
export interface AdminLoan {
  id: number;

  loan_type: string;
  loan_amount: string;
  duration: number;
  interest: number;
  emi: string;

  current_loan_status: LoanStatus;

  user_id: number;
  first_name: string;
  last_name: string;
  email: string;
}
export interface AdminCard {
  id: number;
  account_id: number;

  card_number: string;
  cvc: string;
  expiry_date: string;
  status: CardStatus;
  created_at: string;

  // Customer details returned by admin API
  user_id: number;
  first_name: string;
  last_name: string;
  email: string;
}

export type PanelKey = "dashboard" | "users" | "accounts" | "loans" | "cards";

export type UserStatus = "PENDING" | "APPROVED" | "REJECTED";

export interface AdminUser {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  dob?: string;
  address_line?: string;
  city?: string;
  county?: string;
  postcode?: string;
  mobile?: string;
  rejection_reason?: string | null;
  is_deleted: boolean;
  user_status: UserStatus;
}
export type CardStatus = "ACTIVE" | "FROZEN" | "CLOSED";
