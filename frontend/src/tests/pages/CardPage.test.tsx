import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import CardPage from "../../pages/CardPage";

import {
  getUserCard,
  getUnmaskedCard,
  createCard,
  toggleCardStatus,
} from "../../api/cardClient";

vi.mock("../../api/cardClient", () => ({
  getUserCard: vi.fn(),
  getUnmaskedCard: vi.fn(),
  createCard: vi.fn(),
  toggleCardStatus: vi.fn(),
}));

vi.mock("../../components/Card/CardVisual", () => ({
  default: () => <div data-testid="card-visual">Card Visual</div>,
}));

vi.mock("../../components/Card/CardDetails", () => ({
  default: ({ cardStatus }: { cardStatus: string }) => (
    <div data-testid="card-details">Card Details: {cardStatus}</div>
  ),
}));

vi.mock("../../components/Card/CardActions", () => ({
  default: ({
    cardStatus,
    updatingStatus,
    cardDetailsVisible,
    onShowDetails,
    onHideDetails,
    onToggleStatus,
    onOrderCard,
  }: {
    cardStatus: string;
    updatingStatus: boolean;
    cardDetailsVisible: boolean;
    onShowDetails: () => void;
    onHideDetails: () => void;
    onToggleStatus: () => void;
    onOrderCard: () => void;
  }) => (
    <div data-testid="card-actions">
      <span>{cardStatus}</span>

      <button onClick={onShowDetails}>Show card details</button>

      <button onClick={onHideDetails}>Hide card details</button>

      <button onClick={onToggleStatus} disabled={updatingStatus}>
        Toggle status
      </button>

      <button onClick={onOrderCard}>Order new card</button>

      {cardDetailsVisible && <span>Details visible</span>}
    </div>
  ),
}));

vi.mock("../../components/Card/PasswordModal", () => ({
  default: ({
    password,
    passwordError,
    unmasking,
    onPasswordChange,
    onConfirm,
    onClose,
  }: {
    password: string;
    passwordError: string | null;
    unmasking: boolean;
    onPasswordChange: (password: string) => void;
    onConfirm: () => void;
    onClose: () => void;
  }) => (
    <div data-testid="password-modal">
      <input
        placeholder="Password"
        value={password}
        onChange={(event) => onPasswordChange(event.target.value)}
      />

      {passwordError && <div>{passwordError}</div>}

      <button onClick={onConfirm}>
        {unmasking ? "Verifying..." : "Confirm"}
      </button>

      <button onClick={onClose}>Cancel</button>
    </div>
  ),
}));

vi.mock("../../components/Card/OrderCardModal", () => ({
  default: ({
    ordering,
    onConfirm,
    onClose,
  }: {
    ordering: boolean;
    onConfirm: () => void;
    onClose: () => void;
  }) => (
    <div data-testid="order-card-modal">
      <button onClick={onConfirm}>
        {ordering ? "Ordering..." : "Order new card"}
      </button>

      <button onClick={onClose}>Cancel</button>
    </div>
  ),
}));

vi.mock("react-router", () => ({
  Link: ({ children }: { children: React.ReactNode }) => (
    <a href="/account">{children}</a>
  ),
}));

describe("CardPage", () => {
  const card = {
    card_number: "**** **** **** 1234",
    expiry_date: "12/29",
    cvc: "***",
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("loading", () => {
    it("displays loading state while card is being fetched", () => {
      vi.mocked(getUserCard).mockReturnValue(new Promise(() => {}));

      render(<CardPage />);

      expect(screen.getByText("Loading card...")).toBeInTheDocument();
    });
  });

  describe("loading card", () => {
    it("displays the card after loading successfully", async () => {
      vi.mocked(getUserCard).mockResolvedValue(card);

      render(<CardPage />);

      expect(await screen.findByTestId("card-visual")).toBeInTheDocument();

      expect(screen.getByTestId("card-details")).toHaveTextContent("ACTIVE");
    });

    it("displays an error when loading the card fails", async () => {
      vi.mocked(getUserCard).mockRejectedValue(
        new Error("Failed to load card"),
      );

      render(<CardPage />);

      expect(
        await screen.findByText("Failed to load card"),
      ).toBeInTheDocument();
    });
  });

  describe("showing card details", () => {
    it("opens the password modal", async () => {
      vi.mocked(getUserCard).mockResolvedValue(card);

      const user = userEvent.setup();

      render(<CardPage />);

      await screen.findByTestId("card-visual");

      await user.click(
        screen.getByRole("button", {
          name: "Show card details",
        }),
      );

      expect(screen.getByTestId("password-modal")).toBeInTheDocument();
    });

    it("shows a validation error when confirming without a password", async () => {
      vi.mocked(getUserCard).mockResolvedValue(card);

      const user = userEvent.setup();

      render(<CardPage />);

      await screen.findByTestId("card-visual");

      await user.click(
        screen.getByRole("button", {
          name: "Show card details",
        }),
      );

      await user.click(
        screen.getByRole("button", {
          name: "Confirm",
        }),
      );

      expect(
        screen.getByText("Please enter your password."),
      ).toBeInTheDocument();

      expect(getUnmaskedCard).not.toHaveBeenCalled();
    });

    it("unmasks the card with a valid password", async () => {
      vi.mocked(getUserCard).mockResolvedValue(card);

      const unmaskedCard = {
        card_number: "1234567890123456",
        expiry_date: "12/29",
        cvc: "123",
      };

      vi.mocked(getUnmaskedCard).mockResolvedValue(unmaskedCard);

      const user = userEvent.setup();

      render(<CardPage />);

      await screen.findByTestId("card-visual");

      await user.click(
        screen.getByRole("button", {
          name: "Show card details",
        }),
      );

      await user.type(screen.getByPlaceholderText("Password"), "password123");

      await user.click(
        screen.getByRole("button", {
          name: "Confirm",
        }),
      );

      await waitFor(() => {
        expect(getUnmaskedCard).toHaveBeenCalledWith("password123");
      });

      expect(screen.queryByTestId("password-modal")).not.toBeInTheDocument();

      expect(screen.getByText("Details visible")).toBeInTheDocument();
    });

    it("displays an error when unmasking fails", async () => {
      vi.mocked(getUserCard).mockResolvedValue(card);

      vi.mocked(getUnmaskedCard).mockRejectedValue(
        new Error("Incorrect password"),
      );

      const user = userEvent.setup();

      render(<CardPage />);

      await screen.findByTestId("card-visual");

      await user.click(
        screen.getByRole("button", {
          name: "Show card details",
        }),
      );

      await user.type(
        screen.getByPlaceholderText("Password"),
        "wrong-password",
      );

      await user.click(
        screen.getByRole("button", {
          name: "Confirm",
        }),
      );

      expect(await screen.findByText("Incorrect password")).toBeInTheDocument();
    });
  });

  describe("hiding card details", () => {
    it("loads the masked card and hides details", async () => {
      vi.mocked(getUserCard).mockResolvedValue(card);

      const user = userEvent.setup();

      render(<CardPage />);

      await screen.findByTestId("card-visual");

      await user.click(
        screen.getByRole("button", {
          name: "Hide card details",
        }),
      );

      expect(getUserCard).toHaveBeenCalledTimes(2);

      expect(screen.queryByText("Details visible")).not.toBeInTheDocument();
    });

    it("displays an error when hiding details fails", async () => {
      vi.mocked(getUserCard)
        .mockResolvedValueOnce(card)
        .mockRejectedValueOnce(new Error("Failed to hide card details"));

      const user = userEvent.setup();

      render(<CardPage />);

      await screen.findByTestId("card-visual");

      await user.click(
        screen.getByRole("button", {
          name: "Hide card details",
        }),
      );

      expect(
        await screen.findByText("Failed to hide card details"),
      ).toBeInTheDocument();
    });
  });

  describe("card status", () => {
    it("freezes an active card", async () => {
      vi.mocked(getUserCard).mockResolvedValue(card);

      vi.mocked(toggleCardStatus).mockResolvedValue({
        status: "Frozen.",
      });

      const user = userEvent.setup();

      render(<CardPage />);

      await screen.findByTestId("card-visual");

      await user.click(
        screen.getByRole("button", {
          name: "Toggle status",
        }),
      );

      expect(await screen.findByTestId("card-details")).toHaveTextContent(
        "FROZEN",
      );
    });

    it("activates a frozen card", async () => {
      vi.mocked(getUserCard).mockResolvedValue(card);

      vi.mocked(toggleCardStatus).mockResolvedValue({
        status: "Activated.",
      });

      const user = userEvent.setup();

      render(<CardPage />);

      await screen.findByTestId("card-visual");

      // The page starts ACTIVE, so first freeze it.
      await user.click(
        screen.getByRole("button", {
          name: "Toggle status",
        }),
      );

      await waitFor(() => {
        expect(screen.getByTestId("card-details")).toHaveTextContent("FROZEN");
      });

      // Then activate it.
      await user.click(
        screen.getByRole("button", {
          name: "Toggle status",
        }),
      );

      await waitFor(() => {
        expect(screen.getByTestId("card-details")).toHaveTextContent("ACTIVE");
      });
    });

    it("displays an error when status update fails", async () => {
      vi.mocked(getUserCard).mockResolvedValue(card);

      vi.mocked(toggleCardStatus).mockRejectedValue(
        new Error("Failed to update card status"),
      );

      const user = userEvent.setup();

      render(<CardPage />);

      await screen.findByTestId("card-visual");

      await user.click(
        screen.getByRole("button", {
          name: "Toggle status",
        }),
      );

      expect(
        await screen.findByText("Failed to update card status"),
      ).toBeInTheDocument();
    });
  });

  describe("ordering a card", () => {
    it("opens the order confirmation modal", async () => {
      vi.mocked(getUserCard).mockResolvedValue(card);

      const user = userEvent.setup();

      render(<CardPage />);

      await screen.findByTestId("card-visual");

      await user.click(
        screen.getByRole("button", {
          name: "Order new card",
        }),
      );

      expect(screen.getByTestId("order-card-modal")).toBeInTheDocument();
    });

    it("creates a new card successfully", async () => {
      vi.mocked(getUserCard).mockResolvedValue(card);
      vi.mocked(createCard).mockResolvedValue({
        id: 1,
        account_id: 1,
        card_number: "1234567890123456",
        expiry_date: "12/29",
        cvc: "123",
        status: "ACTIVE",
        created_at: "2026-01-01",
      });

      const user = userEvent.setup();

      render(<CardPage />);

      await screen.findByTestId("card-visual");

      await user.click(
        screen.getByRole("button", {
          name: "Order new card",
        }),
      );

      await user.click(
        screen.getByRole("button", {
          name: "Order new card",
        }),
      );

      await waitFor(() => {
        expect(createCard).toHaveBeenCalledOnce();
      });

      expect(screen.queryByTestId("order-card-modal")).not.toBeInTheDocument();

      expect(screen.getByTestId("card-details")).toHaveTextContent("ACTIVE");
    });

    it("displays an error when creating a card fails", async () => {
      vi.mocked(getUserCard).mockResolvedValue(card);

      vi.mocked(createCard).mockRejectedValue(
        new Error("Failed to create card"),
      );

      const user = userEvent.setup();

      render(<CardPage />);

      await screen.findByTestId("card-visual");

      await user.click(
        screen.getByRole("button", {
          name: "Order new card",
        }),
      );

      await user.click(
        screen.getByRole("button", {
          name: "Order new card",
        }),
      );

      expect(
        await screen.findByText("Failed to create card"),
      ).toBeInTheDocument();
    });
  });
});
