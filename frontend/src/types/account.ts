export interface Account {
  id: number;
  user_id: number;
  balance: string;
  account_number: string | null;
  sort_code: string | null;
  account_status: string | null;
  opened_at: string | null;
  closed_at: string | null;
}
