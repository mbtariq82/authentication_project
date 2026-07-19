import { getAccessToken } from "../auth/tokenStorage";
import { refreshTokens } from "./authClient";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export type UserResponse = {
  id: number;
  username: string;
  role: string;
  is_active: boolean;
};

async function requestCurrentUser(): Promise<Response> {
  const accessToken = getAccessToken();

  if (!accessToken) {
    throw new Error("No access token available");
  }

  return fetch(`${API_BASE_URL}/users/me`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });
}

export async function getCurrentUser(): Promise<UserResponse> {
  let response = await requestCurrentUser();

  if (response.status === 401) {
    await refreshTokens();

    response = await requestCurrentUser();
  }

  if (!response.ok) {
    throw new Error(`Failed to get current user: ${response.status}`);
  }

  return response.json();
}