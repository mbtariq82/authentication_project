import { getAccessToken } from "../auth/tokenStorage";
import { fetchWithAuth, getApiErrorMessage } from "./apiClient";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
const GUEST_SESSION_ID_KEY = "chatbot_guest_session_id";

type ChatResponse = {
  answer: string;
};

function getGuestSessionId(): string {
  const existingSessionId = localStorage.getItem(GUEST_SESSION_ID_KEY);
  if (existingSessionId) {
    return existingSessionId;
  }

  const guestSessionId = crypto.randomUUID();
  localStorage.setItem(GUEST_SESSION_ID_KEY, guestSessionId);
  return guestSessionId;
}

export function resetGuestChatSession(): void {
  localStorage.removeItem(GUEST_SESSION_ID_KEY);
}

export async function sendChatMessage(message: string): Promise<string> {
  const isAuthenticated = Boolean(getAccessToken());
  const response = isAuthenticated
    ? await fetchWithAuth(`${API_BASE_URL}/chatbot/customer`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      })
    : await fetch(`${API_BASE_URL}/chatbot/public`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message,
          guest_session_id: getGuestSessionId(),
        }),
      });

  if (!response.ok) {
    throw new Error(
      await getApiErrorMessage(response, "Unable to send your message."),
    );
  }

  const data = (await response.json()) as ChatResponse;
  return data.answer;
}
