export type TransactionType = "TRANSFER" | "DEPOSIT" | "WITHDRAWAL";

export type TransactionDirection = "DEBIT" | "CREDIT";

export type TransactionStatus =
  | "PENDING"
  | "COMPLETED"
  | "FAILED"
  | "CANCELLED";

// PostgreSQL Decimal values are serialized by FastAPI as strings.
export interface Transaction {
  id: number;
  account_id: number;
  beneficiary_id: number | null;
  transaction_type: TransactionType;
  direction: TransactionDirection;
  amount: string;
  status: TransactionStatus;
  reference: string;
  transfer_reference: string | null;
  description: string | null;
  created_at: string;
  updated_at: string;
}

export interface CreateTransactionRequest {
  account_id: number;
  beneficiary_id?: number | null;
  transaction_type: TransactionType;
  direction: TransactionDirection;
  amount: string;
  transfer_reference?: string | null;
  description?: string | null;
}

export interface TransactionFilters {
  status?: TransactionStatus;
  transaction_type?: TransactionType;
  direction?: TransactionDirection;
  reference?: string;
  created_from?: string;
  created_to?: string;
  offset?: number;
  limit?: number;
}

export interface TransactionLog {
  id: number;
  transaction_id: number;
  user_id: number | null;
  action: string;
  status: string;
  message: string | null;
  metadata: Record<string, unknown> | null;
  created_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  offset: number;
  limit: number;
  total: number;
}
