import { getAccessToken } from "../auth/tokenStorage";
import { refreshTokens } from "./authClient";

async function performRequest(
  input: RequestInfo,
  init: RequestInit = {},
): Promise<Response> {
  const accessToken = getAccessToken();

  return fetch(input, {
    ...init,
    headers: {
      ...init.headers,
      Authorization: accessToken ? `Bearer ${accessToken}` : "",
    },
  });
}

export async function fetchWithAuth(
  input: RequestInfo,
  init: RequestInit = {},
): Promise<Response> {
  let response = await performRequest(input, init);

  if (response.status !== 401) {
    return response;
  }

  await refreshTokens();

  response = await performRequest(input, init);

  return response;
}