import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import CardActions from "../../../components/Card/CardActions";

describe("CardActions", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  const defaultProps = {
    cardStatus: "ACTIVE" as const,
    updatingStatus: false,
    cardDetailsVisible: false,
    onShowDetails: vi.fn(),
    onHideDetails: vi.fn(),
    onToggleStatus: vi.fn(),
    onOrderCard: vi.fn(),
  };

  describe("card details button", () => {
    it("shows 'Show card details' when details are hidden", () => {
      render(<CardActions {...defaultProps} />);

      expect(
        screen.getByRole("button", {
          name: "Show card details",
        }),
      ).toBeInTheDocument();
    });

    it("shows 'Hide' when details are visible", () => {
      render(<CardActions {...defaultProps} cardDetailsVisible={true} />);

      expect(
        screen.getByRole("button", {
          name: "Hide",
        }),
      ).toBeInTheDocument();
    });

    it("calls onShowDetails when details are hidden", async () => {
      const user = userEvent.setup();

      render(<CardActions {...defaultProps} />);

      await user.click(
        screen.getByRole("button", {
          name: "Show card details",
        }),
      );

      expect(defaultProps.onShowDetails).toHaveBeenCalledOnce();
      expect(defaultProps.onHideDetails).not.toHaveBeenCalled();
    });

    it("calls onHideDetails when details are visible", async () => {
      const user = userEvent.setup();

      render(<CardActions {...defaultProps} cardDetailsVisible={true} />);

      await user.click(
        screen.getByRole("button", {
          name: "Hide",
        }),
      );

      expect(defaultProps.onHideDetails).toHaveBeenCalledOnce();
      expect(defaultProps.onShowDetails).not.toHaveBeenCalled();
    });
  });

  describe("freeze button", () => {
    it("shows 'Freeze card' when the card is active", () => {
      render(<CardActions {...defaultProps} />);

      expect(
        screen.getByRole("button", {
          name: "Freeze card",
        }),
      ).toBeInTheDocument();
    });

    it("shows 'Unfreeze card' when the card is frozen", () => {
      render(<CardActions {...defaultProps} cardStatus="FROZEN" />);

      expect(
        screen.getByRole("button", {
          name: "Unfreeze card",
        }),
      ).toBeInTheDocument();
    });

    it("calls onToggleStatus when clicked", async () => {
      const user = userEvent.setup();

      render(<CardActions {...defaultProps} />);

      await user.click(
        screen.getByRole("button", {
          name: "Freeze card",
        }),
      );

      expect(defaultProps.onToggleStatus).toHaveBeenCalledOnce();
    });

    it("disables the button while updating", () => {
      render(<CardActions {...defaultProps} updatingStatus={true} />);

      const button = screen.getByRole("button", {
        name: "Updating...",
      });

      expect(button).toBeDisabled();
    });

    it("shows 'Updating...' while updating", () => {
      render(<CardActions {...defaultProps} updatingStatus={true} />);

      expect(
        screen.getByRole("button", {
          name: "Updating...",
        }),
      ).toBeInTheDocument();
    });
  });

  describe("order card button", () => {
    it("shows 'Order new card'", () => {
      render(<CardActions {...defaultProps} />);

      expect(
        screen.getByRole("button", {
          name: "Order new card",
        }),
      ).toBeInTheDocument();
    });

    it("calls onOrderCard when clicked", async () => {
      const user = userEvent.setup();

      render(<CardActions {...defaultProps} />);

      await user.click(
        screen.getByRole("button", {
          name: "Order new card",
        }),
      );

      expect(defaultProps.onOrderCard).toHaveBeenCalledOnce();
    });
  });
});
