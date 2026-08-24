import type { AdminAgentAskResponse } from "../types/admin";

import { fetchWithAuth, type ApiErrorResponse } from "./apiClient";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

async function handle<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorData = (await response
      .json()
      .catch(() => ({}))) as ApiErrorResponse;

    throw new Error(
      errorData.detail ?? `Request failed with status ${response.status}`,
    );
  }

  return response.json() as Promise<T>;
}

// ---------------- ADMIN AI ASSISTANT ----------------

export async function askAdminAgent(
  question: string,
): Promise<AdminAgentAskResponse> {
  const response = await fetchWithAuth(`${API_BASE_URL}/admin/ask`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ question }),
  });

  return handle<AdminAgentAskResponse>(response);
}

export async function exportAdminAgentResult(question: string): Promise<void> {
  const response = await fetchWithAuth(`${API_BASE_URL}/admin/ask/export`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ question }),
  });

  if (!response.ok) {
    const errorData = (await response
      .json()
      .catch(() => ({}))) as ApiErrorResponse;

    throw new Error(
      errorData.detail ?? `Export failed with status ${response.status}`,
    );
  }

  const blob = await response.blob();

  // Read the filename FastAPI's Content-Disposition header sent us,
  // falling back to a generic name if it's missing for some reason.
  const disposition = response.headers.get("Content-Disposition") ?? "";
  const match = disposition.match(/filename="?([^"]+)"?/);
  const filename = match?.[1] ?? "admin_query_result.xlsx";

  const objectUrl = window.URL.createObjectURL(blob);
  const link = document.createElement("a");

  link.href = objectUrl;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();

  window.URL.revokeObjectURL(objectUrl);
}
