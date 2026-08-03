export type Batch = "PYTHON" | "JAVA" | "DATA" | "ANDROID";

export type PlacementStatus =
  | "ONBOARDING"
  | "TRAINING"
  | "AVAILABLE"
  | "PLACED"
  | "ENDING_SOON";

export interface UnassignedUser {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
}

export interface CreateConsultantRequest {
  user_id: number;
  batch: Batch;
  placement_status: PlacementStatus;
  client: string | null;
}

export interface Consultant {
  id: number;
  user_id: number;
  email: string;
  first_name: string;
  last_name: string;
  batch: Batch;
  placement_status: PlacementStatus;
  client: string | null;
}