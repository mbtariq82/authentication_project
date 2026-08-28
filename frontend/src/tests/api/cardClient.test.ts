import { beforeEach, describe, expect, it, vi } from "vitest";

import {
  createCard,
  getUnmaskedCard,
  getUserCard,
  toggleCardStatus,
} from "../../api/cardClient";

import { fetchWithAuth } from "../../api/apiClient";

vi.mock("../../api/apiClient", () => ({
  fetchWithAuth: vi.fn(),
}));

const mockedFetchWithAuth = vi.mocked(fetchWithAuth);

describe("cardClient", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("getUserCard", () => {
    it("returns the user's card", async () => {
      const card = {
        card_number: "**** **** **** 1234",
        expiry_date: "12/29",
        cvc: "***",
      };

      mockedFetchWithAuth.mockResolvedValue(
        new Response(JSON.stringify(card), {
          status: 200,
        }),
      );

      const result = await getUserCard();

      expect(result).toEqual(card);

      expect(mockedFetchWithAuth).toHaveBeenCalledWith(
        expect.stringContaining("/cards"),
      );
    });

    it("throws the API error", async () => {
      mockedFetchWithAuth.mockResolvedValue(
        new Response(
          JSON.stringify({
            detail: "Card not found.",
          }),
          { status: 404 },
        ),
      );

      await expect(getUserCard()).rejects.toThrow("Card not found.");
    });
  });

  describe("getUnmaskedCard", () => {
    it("sends the password", async () => {
      const card = {
        card_number: "1234567890123456",
        expiry_date: "12/29",
        cvc: "123",
      };

      mockedFetchWithAuth.mockResolvedValue(
        new Response(JSON.stringify(card), {
          status: 200,
        }),
      );

      const result = await getUnmaskedCard("password123");

      expect(result).toEqual(card);

      expect(mockedFetchWithAuth).toHaveBeenCalledWith(
        expect.stringContaining("/cards/details"),
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            password: "password123",
          }),
        },
      );
    });

    it("throws the API error", async () => {
      mockedFetchWithAuth.mockResolvedValue(
        new Response(
          JSON.stringify({
            detail: "Incorrect password.",
          }),
          { status: 401 },
        ),
      );

      await expect(getUnmaskedCard("wrong-password")).rejects.toThrow(
        "Incorrect password.",
      );
    });
  });

  describe("createCard", () => {
    it("creates a card", async () => {
      const card = {
        id: 1,
        account_id: 10,
        card_number: "1234567890123456",
        expiry_date: "2029-12-01T00:00:00",
        cvc: "123",
        status: "ACTIVE",
        created_at: "2026-08-20T12:00:00",
      };

      mockedFetchWithAuth.mockResolvedValue(
        new Response(JSON.stringify(card), {
          status: 201,
        }),
      );

      const result = await createCard();

      expect(result).toEqual(card);

      expect(mockedFetchWithAuth).toHaveBeenCalledWith(
        expect.stringContaining("/cards"),
        {
          method: "POST",
        },
      );
    });

    it("throws the API error", async () => {
      mockedFetchWithAuth.mockResolvedValue(
        new Response(
          JSON.stringify({
            detail: "Card already exists.",
          }),
          { status: 400 },
        ),
      );

      await expect(createCard()).rejects.toThrow("Card already exists.");
    });
  });

  describe("toggleCardStatus", () => {
    it("toggles the card status", async () => {
      const response = {
        status: "FROZEN",
      };

      mockedFetchWithAuth.mockResolvedValue(
        new Response(JSON.stringify(response), {
          status: 200,
        }),
      );

      const result = await toggleCardStatus();

      expect(result).toEqual(response);

      expect(mockedFetchWithAuth).toHaveBeenCalledWith(
        expect.stringContaining("/cards/freeze"),
        {
          method: "PATCH",
        },
      );
    });

    it("throws the API error", async () => {
      mockedFetchWithAuth.mockResolvedValue(
        new Response(
          JSON.stringify({
            detail: "Card cannot be frozen.",
          }),
          { status: 400 },
        ),
      );

      await expect(toggleCardStatus()).rejects.toThrow(
        "Card cannot be frozen.",
      );
    });
  });
});
