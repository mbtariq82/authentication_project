export interface Account {
  id: number;
  user_id: number;
  sort_code: string | null;
  branch: string | null;
  account_type: string | null;
  account_number: string | null;
  balance: string;
  account_status: string | null;
  is_deleted: boolean;
  close_reason: string | null;
  closed_at: string | null;
  created_at: string | null;
  updated_at: string | null;
}
