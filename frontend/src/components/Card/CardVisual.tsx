import { useState } from "react";
import { Snowflake } from "lucide-react";
import type { CardDetailsResponse } from "../../api/cardClient";
import { formatCardNumber } from "./CardDetails";
import cardChip from "../../assets/card-chip.png";
import masterCardLogo from "../../assets/Mastercard-logo.png";
type CardVisualProps = {
  card: CardDetailsResponse;
  cardStatus: "ACTIVE" | "FROZEN";
};

export default function CardVisual({ card, cardStatus }: CardVisualProps) {
  const [flipped, setFlipped] = useState(false);
  return (
    <div
      className={`card-visual-container ${
        flipped ? "card-visual-container-flipped" : ""
      }`}
      onClick={() => setFlipped((current) => !current)}
    >
      <div className="card-visual-inner">
        <div
          className={`card-visual card-visual-front ${
            cardStatus === "FROZEN" ? "card-visual-frozen" : ""
          }`}
        >
          <div className="card-visual-header">
            <div>
              <div className="card-brand">Bank Card</div>
              <div className="card-type">Debit</div>
            </div>

            {cardStatus === "FROZEN" ? (
              <Snowflake size={24} />
            ) : (
              <img src={masterCardLogo} alt="" className="logo" />
            )}
          </div>

          <div className="card-number">
            {formatCardNumber(card.card_number)}
          </div>

          <div className="card-visual-footer">
            <div>
              <div className="card-visual-label">Expires</div>
              <div className="card-visual-value">{card.expiry_date}</div>
            </div>
          </div>

          <img src={cardChip} alt="" className="card-chip" />
        </div>

        <div
          className={`card-visual card-visual-back ${
            cardStatus === "FROZEN" ? "card-visual-frozen" : ""
          }`}
        >
          <div className="card-back-stripe" />

          <div className="card-back-cvv">
            <span>CVV</span>
            <div>{card.cvc}</div>
          </div>

          <div className="card-back-footer">
            <span>Nexa Bank</span>
            <span>Debit</span>
          </div>
        </div>
      </div>
    </div>
  );
}
