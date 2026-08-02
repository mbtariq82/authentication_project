import { fetchWithAuth, type ApiErrorResponse } from "./apiClient";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

type UserRole = "USER" | "ADMIN";

export type UserResponse = {
  id: number;
  email: string;
  role: UserRole;
};

export async function getUserProfile(): Promise<UserResponse> {
  const response = await fetchWithAuth(
    `${API_BASE_URL}/users/me`,
  );

  if (!response.ok) {
    const errorData =
      (await response.json()) as ApiErrorResponse;

    throw new Error(
      errorData.detail ?? "Failed to load current user.",
    );
  }

  return response.json() as Promise<UserResponse>;
}