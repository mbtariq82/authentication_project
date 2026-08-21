import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";

import CardDetails, {
  formatCardNumber,
} from "../../../components/Card/CardDetails";

describe("formatCardNumber", () => {
  it("formats a card number into groups of four", () => {
    expect(formatCardNumber("1234567890123456")).toBe("1234 5678 9012 3456");
  });

  it("formats a shorter card number", () => {
    expect(formatCardNumber("12345678")).toBe("1234 5678");
  });

  it("handles a card number that is not divisible by four", () => {
    expect(formatCardNumber("123456789")).toBe("1234 5678 9");
  });

  it("returns an empty string for an empty card number", () => {
    expect(formatCardNumber("")).toBe("");
  });
});

describe("CardDetails", () => {
  const card = {
    card_number: "1234567890123456",
    expiry_date: "12/29",
    cvc: "123",
  };

  it("renders the card details", () => {
    render(<CardDetails card={card} cardStatus="ACTIVE" />);

    expect(
      screen.getByRole("heading", {
        name: "Card details",
      }),
    ).toBeInTheDocument();

    expect(screen.getByText("1234 5678 9012 3456")).toBeInTheDocument();
    expect(screen.getByText("12/29")).toBeInTheDocument();
    expect(screen.getByText("123")).toBeInTheDocument();
  });

  it("displays the active status", () => {
    render(<CardDetails card={card} cardStatus="ACTIVE" />);

    expect(screen.getAllByText("ACTIVE")).toHaveLength(1);
    expect(screen.getByText("active")).toBeInTheDocument();
  });

  it("displays the frozen status", () => {
    render(<CardDetails card={card} cardStatus="FROZEN" />);

    expect(screen.getByText("FROZEN")).toBeInTheDocument();
    expect(screen.getByText("frozen")).toBeInTheDocument();
  });

  it("formats the card number before displaying it", () => {
    render(
      <CardDetails
        card={{
          ...card,
          card_number: "9876543210987654",
        }}
        cardStatus="ACTIVE"
      />,
    );

    expect(screen.getByText("9876 5432 1098 7654")).toBeInTheDocument();
  });
});
