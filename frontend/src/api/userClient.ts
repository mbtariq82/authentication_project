import { fetchWithAuth, type ApiErrorResponse } from "./apiClient";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

type UserRole = "USER" | "ADMIN";

export type UserResponse = {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  role: UserRole;
  profile_image_url: string | null;
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

  const user = (await response.json()) as UserResponse;

  return {
    ...user,
    profile_image_url: user.profile_image_url
      ? new URL(user.profile_image_url, `${API_BASE_URL}/`).toString()
      : null,
  };
}
