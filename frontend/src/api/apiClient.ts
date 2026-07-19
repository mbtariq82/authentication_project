import { getAccessToken } from "../auth/tokenStorage";

export async function apiFetch(
  input: RequestInfo,
  init: RequestInit = {},
) {
  const token = getAccessToken();

  return fetch(input, {
    ...init,
    headers: {
      ...init.headers,
      Authorization: token ? `Bearer ${token}` : "",
    },
  });
}