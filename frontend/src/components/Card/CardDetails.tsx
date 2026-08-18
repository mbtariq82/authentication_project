import type { CardDetailsResponse } from "../../api/cardClient";

type CardDetailsProps = {
  card: CardDetailsResponse;
  cardStatus: "ACTIVE" | "FROZEN";
};

export function formatCardNumber(cardNumber: string): string {
  return cardNumber.match(/.{1,4}/g)?.join(" ") ?? cardNumber;
}

export default function CardDetails({ card, cardStatus }: CardDetailsProps) {
  return (
    <section className="card-panel">
      <div className="card-panel-header">
        <h2 className="card-panel-title">Card details</h2>

        <span className={`card-status ${cardStatus.toLowerCase()}`}>
          {cardStatus.toLowerCase()}
        </span>
      </div>

      <div className="card-details">
        <div className="card-detail">
          <div className="card-detail-label">Card number</div>
          <div className="card-detail-value">
            {formatCardNumber(card.card_number)}
          </div>
        </div>

        <div className="card-detail">
          <div className="card-detail-label">Expiry date</div>
          <div className="card-detail-value">{card.expiry_date}</div>
        </div>

        <div className="card-detail">
          <div className="card-detail-label">CVC</div>
          <div className="card-detail-value">{card.cvc}</div>
        </div>

        <div className="card-detail">
          <div className="card-detail-label">Status</div>
          <div className="card-detail-value">{cardStatus}</div>
        </div>
      </div>
    </section>
  );
}
