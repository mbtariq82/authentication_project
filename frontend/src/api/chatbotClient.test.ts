import { beforeEach, describe, expect, it, vi } from "vitest";

import { resetGuestChatSession, sendChatMessage } from "./chatbotClient";

const storage = new Map<string, string>();

function makeResponse(answer: string): Response {
  return new Response(JSON.stringify({ answer }), { status: 200 });
}

describe("chatbot client", () => {
  beforeEach(() => {
    storage.clear();
    vi.stubGlobal("localStorage", {
      getItem: (key: string) => storage.get(key) ?? null,
      removeItem: (key: string) => storage.delete(key),
      setItem: (key: string, value: string) => storage.set(key, value),
    });
    vi.stubGlobal("crypto", { randomUUID: vi.fn(() => "guest-session-id") });
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(makeResponse("Public answer")),
    );
  });

  it("sends guests to the public endpoint with a persistent session ID", async () => {
    await expect(sendChatMessage("Hello")).resolves.toBe("Public answer");
    await expect(sendChatMessage("Tell me more")).resolves.toBe(
      "Public answer",
    );

    expect(fetch).toHaveBeenCalledTimes(2);
    const [firstUrl, firstRequest] = vi.mocked(fetch).mock.calls[0];
    const [, secondRequest] = vi.mocked(fetch).mock.calls[1];
    expect(firstUrl).toContain("/chatbot/public");
    expect(JSON.parse(String(firstRequest?.body))).toMatchObject({
      guest_session_id: "guest-session-id",
      message: "Hello",
    });
    expect(JSON.parse(String(secondRequest?.body))).toMatchObject({
      guest_session_id: "guest-session-id",
      message: "Tell me more",
    });
  });

  it("clears the guest session when a chat is closed", async () => {
    await sendChatMessage("Hello");
    resetGuestChatSession();

    expect(storage.has("chatbot_guest_session_id")).toBe(false);
  });
});
