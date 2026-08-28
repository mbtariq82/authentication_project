import { describe, expect, it } from "vitest";

import { getApiErrorMessage } from "../../api/apiClient";

describe("getApiErrorMessage", () => {
  it("reads a backend detail message", async () => {
    const response = new Response(
      JSON.stringify({ detail: "Insufficient funds" }),
      { status: 409 },
    );

    await expect(
      getApiErrorMessage(response, "Fallback message"),
    ).resolves.toBe("Insufficient funds");
  });

  it("uses the fallback for an empty response", async () => {
    const response = new Response(null, { status: 500 });

    await expect(getApiErrorMessage(response, "Request failed")).resolves.toBe(
      "Request failed",
    );
  });
});
