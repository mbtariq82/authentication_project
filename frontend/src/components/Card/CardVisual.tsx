import { Snowflake } from "lucide-react";
import type { CardDetailsResponse } from "../../api/cardClient";
import cardChip from "../../assets/card-chip.png";
import masterCardLogo from "../../assets/Mastercard-logo.png";
type CardVisualProps = {
  card: CardDetailsResponse;
  cardStatus: "ACTIVE" | "FROZEN";
};

export default function CardVisual({ card, cardStatus }: CardVisualProps) {
  return (
    <div
      className={`card-visual ${
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

      <img src={cardChip} alt="" className="card-chip" />

      <div className="card-visual-footer">
        <div>
          <div className="card-visual-label">Expires</div>
          <div className="card-visual-value">{card.expiry_date}</div>
        </div>
      </div>
    </div>
  );
}
