import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import CardVisual from "../../../components/Card/CardVisual";

describe("CardVisual", () => {
  const card = {
    card_number: "1234567890123456",
    expiry_date: "12/29",
    cvc: "123",
  };

  describe("card information", () => {
    it("displays the formatted card number", () => {
      render(<CardVisual card={card} cardStatus="ACTIVE" />);

      expect(screen.getByText("1234 5678 9012 3456")).toBeInTheDocument();
    });

    it("displays the expiry date", () => {
      render(<CardVisual card={card} cardStatus="ACTIVE" />);

      expect(screen.getByText("12/29")).toBeInTheDocument();
    });

    it("displays the CVC", () => {
      render(<CardVisual card={card} cardStatus="ACTIVE" />);

      expect(screen.getByText("123")).toBeInTheDocument();
    });
  });

  describe("active card", () => {
    it("displays the Mastercard logo", () => {
      const { container } = render(
        <CardVisual card={card} cardStatus="ACTIVE" />,
      );

      const logo = container.querySelector("img.logo");

      expect(logo).toBeInTheDocument();
    });

    it("does not display the frozen styling", () => {
      const { container } = render(
        <CardVisual card={card} cardStatus="ACTIVE" />,
      );

      expect(
        container.querySelector(".card-visual-frozen"),
      ).not.toBeInTheDocument();
    });
  });

  describe("frozen card", () => {
    it("does not display the Mastercard logo", () => {
      render(<CardVisual card={card} cardStatus="FROZEN" />);

      expect(screen.queryByAltText("")).not.toHaveClass("logo");
    });

    it("applies the frozen styling", () => {
      const { container } = render(
        <CardVisual card={card} cardStatus="FROZEN" />,
      );

      expect(container.querySelectorAll(".card-visual-frozen")).toHaveLength(2);
    });
  });

  describe("card flipping", () => {
    it("starts with the card facing the front", () => {
      const { container } = render(
        <CardVisual card={card} cardStatus="ACTIVE" />,
      );

      expect(
        container.querySelector(".card-visual-container-flipped"),
      ).not.toBeInTheDocument();
    });

    it("flips the card when clicked", async () => {
      const user = userEvent.setup();

      const { container } = render(
        <CardVisual card={card} cardStatus="ACTIVE" />,
      );

      const cardContainer = container.querySelector(".card-visual-container");

      expect(cardContainer).toBeInTheDocument();

      await user.click(cardContainer!);

      expect(
        container.querySelector(".card-visual-container-flipped"),
      ).toBeInTheDocument();
    });

    it("flips the card back when clicked again", async () => {
      const user = userEvent.setup();

      const { container } = render(
        <CardVisual card={card} cardStatus="ACTIVE" />,
      );

      const cardContainer = container.querySelector(".card-visual-container");

      await user.click(cardContainer!);

      expect(
        container.querySelector(".card-visual-container-flipped"),
      ).toBeInTheDocument();

      await user.click(cardContainer!);

      expect(
        container.querySelector(".card-visual-container-flipped"),
      ).not.toBeInTheDocument();
    });
  });
});
