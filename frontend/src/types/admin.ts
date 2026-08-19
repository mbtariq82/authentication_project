export type LoanStatus =
  | "pending"
  | "approved"
  | "rejected"
  | "cancelled"
  | "closed";
export type CardStatus = "active" | "frozen" | "expired" | "cancel";

export type AccountStatus =
  | "PENDING"
  | "APPROVED"
  | "FROZEN"
  | "CLOSED"
  | "REJECTED";

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
// export type UserStatus = "PENDING" | "APPROVED" | "REJECTED";

// export interface AdminUser {
//   id: number;
//   email: string;
//   first_name: string;
//   last_name: string;
//   role: string;
//   user_status: UserStatus;
// }

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
