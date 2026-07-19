import {
  getRefreshToken,
  saveTokens
} from "../auth/tokenStorage";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export type LoginCredentials = {
  username: string;
  password: string;
};

export type TokenResponse = {
  access_token: string;
  refresh_token: string;
  token_type: string;
};

type ApiErrorResponse = {
  detail?: string;
};

let refreshPromise: Promise<void> | null = null;

export async function login(
  credentials: LoginCredentials,
): Promise<TokenResponse> {
  const formData = new URLSearchParams();

  formData.append("username", credentials.username);
  formData.append("password", credentials.password);

  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: formData,
  });

  if (!response.ok) {
    const errorData = (await response.json()) as ApiErrorResponse;

    throw new Error(errorData.detail ?? "Login failed.");
  }

  return response.json() as Promise<TokenResponse>;
}

export async function revokeRefreshToken(): Promise<void> {
  const refreshToken = getRefreshToken();

  if (!refreshToken) {
    return;
  }

  const response = await fetch(`${API_BASE_URL}/auth/logout`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      token: refreshToken,
    }),
  });

  if (!response.ok) {
    throw new Error(`Logout failed: ${response.status}`);
  }
}

async function performTokenRefresh(): Promise<void> {
  const refreshToken = getRefreshToken();

  if (!refreshToken) {
    throw new Error("No refresh token available");
  }

  const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      token: refreshToken,
    }),
  });

  if (!response.ok) {
    const errorData = (await response.json()) as ApiErrorResponse;

    throw new Error(
      errorData.detail ?? `Token refresh failed: ${response.status}`,
    );
  }

  const tokens = (await response.json()) as TokenResponse;

  saveTokens(tokens);
}

export function refreshTokens(): Promise<void> {
  if (!refreshPromise) {
    refreshPromise = performTokenRefresh().finally(() => {
      refreshPromise = null;
    });
  }

  return refreshPromise;
}