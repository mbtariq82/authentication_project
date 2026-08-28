import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useState } from "react";

import PasswordModal from "../../../components/Card/PasswordModal";

describe("PasswordModal", () => {
  const createProps = () => ({
    password: "",
    passwordError: null,
    unmasking: false,
    onPasswordChange: vi.fn(),
    onConfirm: vi.fn(),
    onClose: vi.fn(),
  });

  describe("modal content", () => {
    it("displays the modal title", () => {
      const props = createProps();

      render(<PasswordModal {...props} />);

      expect(
        screen.getByRole("heading", {
          name: "Enter your password",
        }),
      ).toBeInTheDocument();
    });

    it("displays the password input", () => {
      const props = createProps();

      render(<PasswordModal {...props} />);

      expect(screen.getByPlaceholderText("Password")).toBeInTheDocument();
    });

    it("renders the password input as a password field", () => {
      const props = createProps();

      render(<PasswordModal {...props} />);

      expect(screen.getByPlaceholderText("Password")).toHaveAttribute(
        "type",
        "password",
      );
    });

    it("displays the Cancel button", () => {
      const props = createProps();

      render(<PasswordModal {...props} />);

      expect(
        screen.getByRole("button", {
          name: "Cancel",
        }),
      ).toBeInTheDocument();
    });

    it("displays the Confirm button", () => {
      const props = createProps();

      render(<PasswordModal {...props} />);

      expect(
        screen.getByRole("button", {
          name: "Confirm",
        }),
      ).toBeInTheDocument();
    });
  });

  describe("password input", () => {
    it("displays the provided password", () => {
      const props = createProps();

      render(<PasswordModal {...props} password="password123" />);

      expect(screen.getByPlaceholderText("Password")).toHaveValue(
        "password123",
      );
    });

    it("updates the password when the user types", async () => {
      const user = userEvent.setup();

      function TestWrapper() {
        const [password, setPassword] = useState("");

        return (
          <PasswordModal
            password={password}
            passwordError={null}
            unmasking={false}
            onPasswordChange={setPassword}
            onConfirm={vi.fn()}
            onClose={vi.fn()}
          />
        );
      }

      render(<TestWrapper />);

      const input = screen.getByPlaceholderText("Password");

      await user.type(input, "password123");

      expect(input).toHaveValue("password123");
    });
  });

  describe("password error", () => {
    it("does not display an error when passwordError is null", () => {
      const props = createProps();

      render(<PasswordModal {...props} />);

      expect(screen.queryByText("Incorrect password")).not.toBeInTheDocument();
    });

    it("displays the password error", () => {
      const props = createProps();

      render(<PasswordModal {...props} passwordError="Incorrect password" />);

      expect(screen.getByText("Incorrect password")).toBeInTheDocument();
    });
  });

  describe("cancel button", () => {
    it("calls onClose when clicked", async () => {
      const user = userEvent.setup();
      const props = createProps();

      render(<PasswordModal {...props} />);

      await user.click(
        screen.getByRole("button", {
          name: "Cancel",
        }),
      );

      expect(props.onClose).toHaveBeenCalledOnce();
    });
  });

  describe("confirm button", () => {
    it("calls onConfirm when clicked", async () => {
      const user = userEvent.setup();
      const props = createProps();

      render(<PasswordModal {...props} />);

      await user.click(
        screen.getByRole("button", {
          name: "Confirm",
        }),
      );

      expect(props.onConfirm).toHaveBeenCalledOnce();
    });
  });

  describe("unmasking state", () => {
    it("displays 'Verifying...' while unmasking", () => {
      const props = createProps();

      render(<PasswordModal {...props} unmasking={true} />);

      expect(
        screen.getByRole("button", {
          name: "Verifying...",
        }),
      ).toBeInTheDocument();
    });

    it("disables the confirm button while unmasking", () => {
      const props = createProps();

      render(<PasswordModal {...props} unmasking={true} />);

      expect(
        screen.getByRole("button", {
          name: "Verifying...",
        }),
      ).toBeDisabled();
    });
  });
});
