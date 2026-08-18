export interface Beneficiary {
  id: number;
  user_id: number;
  name: string;
  account_number: string;
  sort_code: string;
  bank_name: string;
  reference: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateBeneficiaryRequest {
  name: string;
  account_number: string;
  sort_code: string;
  bank_name: string;
  reference?: string | null;
}

export interface UpdateBeneficiaryRequest {
  name?: string;
  account_number?: string;
  sort_code?: string;
  bank_name?: string;
  reference?: string | null;
  is_active?: boolean;
}
