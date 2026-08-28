import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import OrderCardModal from "../../../components/Card/OrderCardModal";

describe("OrderCardModal", () => {
  const createProps = () => ({
    ordering: false,
    onConfirm: vi.fn(),
    onClose: vi.fn(),
  });

  describe("modal content", () => {
    it("displays the modal title", () => {
      const props = createProps();

      render(<OrderCardModal {...props} />);

      expect(
        screen.getByRole("heading", {
          name: "Order a new card?",
        }),
      ).toBeInTheDocument();
    });

    it("displays the warning message", () => {
      const props = createProps();

      render(<OrderCardModal {...props} />);

      expect(
        screen.getByText(
          /Only use this option if your current card has been lost or stolen/,
        ),
      ).toBeInTheDocument();
    });

    it("displays the Cancel button", () => {
      const props = createProps();

      render(<OrderCardModal {...props} />);

      expect(
        screen.getByRole("button", {
          name: "Cancel",
        }),
      ).toBeInTheDocument();
    });

    it("displays the Order new card button", () => {
      const props = createProps();

      render(<OrderCardModal {...props} />);

      expect(
        screen.getByRole("button", {
          name: "Order new card",
        }),
      ).toBeInTheDocument();
    });
  });

  describe("cancel button", () => {
    it("calls onClose when clicked", async () => {
      const user = userEvent.setup();
      const props = createProps();

      render(<OrderCardModal {...props} />);

      await user.click(
        screen.getByRole("button", {
          name: "Cancel",
        }),
      );

      expect(props.onClose).toHaveBeenCalledOnce();
    });

    it("is enabled when not ordering", () => {
      const props = createProps();

      render(<OrderCardModal {...props} />);

      expect(
        screen.getByRole("button", {
          name: "Cancel",
        }),
      ).toBeEnabled();
    });
  });

  describe("confirm button", () => {
    it("calls onConfirm when clicked", async () => {
      const user = userEvent.setup();
      const props = createProps();

      render(<OrderCardModal {...props} />);

      await user.click(
        screen.getByRole("button", {
          name: "Order new card",
        }),
      );

      expect(props.onConfirm).toHaveBeenCalledOnce();
    });
  });

  describe("ordering state", () => {
    it("displays 'Ordering...' while ordering", () => {
      const props = createProps();

      render(<OrderCardModal {...props} ordering={true} />);

      expect(
        screen.getByRole("button", {
          name: "Ordering...",
        }),
      ).toBeInTheDocument();
    });

    it("disables both buttons while ordering", () => {
      const props = createProps();

      render(<OrderCardModal {...props} ordering={true} />);

      expect(
        screen.getByRole("button", {
          name: "Cancel",
        }),
      ).toBeDisabled();

      expect(
        screen.getByRole("button", {
          name: "Ordering...",
        }),
      ).toBeDisabled();
    });

    it("does not call onConfirm when ordering", async () => {
      const user = userEvent.setup();
      const props = createProps();

      render(<OrderCardModal {...props} ordering={true} />);

      await user.click(
        screen.getByRole("button", {
          name: "Ordering...",
        }),
      );

      expect(props.onConfirm).not.toHaveBeenCalled();
    });

    it("does not call onClose when ordering", async () => {
      const user = userEvent.setup();
      const props = createProps();

      render(<OrderCardModal {...props} ordering={true} />);

      await user.click(
        screen.getByRole("button", {
          name: "Cancel",
        }),
      );

      expect(props.onClose).not.toHaveBeenCalled();
    });
  });
});
