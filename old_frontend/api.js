const API_BASE_URL = "http://127.0.0.1:8000";

let accessToken = null;
let refreshToken = null;

export function isAuthenticated() {
  return accessToken !== null;
}

export function setTokens(tokens) {
  if (!tokens.access_token) {
    throw new Error("The server did not return an access token.");
  }

  accessToken = tokens.access_token;

  /*
   * Your refresh endpoint rotates refresh tokens, so replace the
   * old refresh token whenever a new one is returned.
   */
  if (tokens.refresh_token) {
    refreshToken = tokens.refresh_token;
  }
}

export function clearTokens() {
  accessToken = null;
  refreshToken = null;
}

export async function login(username, password) {
  const formData = new URLSearchParams();

  formData.set("username", username);
  formData.set("password", password);

  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: formData,
  });

  const data = await parseResponse(response);

  if (!response.ok) {
    throw new Error(getErrorMessage(data, "Login failed."));
  }

  setTokens(data);

  return data;
}

export async function refreshTokens() {
  if (!refreshToken) {
    throw new Error("No refresh token is available. Log in again.");
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

  const data = await parseResponse(response);

  if (!response.ok) {
    clearTokens();

    throw new Error(
      getErrorMessage(data, "Your session has expired. Log in again."),
    );
  }

  setTokens(data);

  return data;
}

export async function apiRequest(path, options = {}) {
  const response = await sendAuthenticatedRequest(path, options);

  /*
   * If the access token has expired, refresh it and retry the
   * original request once.
   */
  if (response.status === 401 && refreshToken) {
    await refreshTokens();

    return sendAuthenticatedRequest(path, options);
  }

  return response;
}

async function sendAuthenticatedRequest(path, options = {}) {
  const headers = new Headers(options.headers);

  if (accessToken) {
    headers.set("Authorization", `Bearer ${accessToken}`);
  }

  return fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });
}

export async function parseResponse(response) {
  const contentType = response.headers.get("content-type") ?? "";

  if (contentType.includes("application/json")) {
    return response.json();
  }

  const text = await response.text();

  return text || null;
}

export function getErrorMessage(data, fallbackMessage) {
  if (typeof data === "string" && data.length > 0) {
    return data;
  }

  if (data?.detail) {
    if (typeof data.detail === "string") {
      return data.detail;
    }

    return JSON.stringify(data.detail);
  }

  return fallbackMessage;
}