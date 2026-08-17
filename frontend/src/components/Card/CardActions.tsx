import { Snowflake } from "lucide-react";

type CardActionsProps = {
  cardStatus: "ACTIVE" | "FROZEN";
  updatingStatus: boolean;
  cardDetailsVisible: boolean;
  onShowDetails: () => void;
  onHideDetails: () => void;
  onToggleStatus: () => void;
  onOrderCard: () => void;
};

export default function CardActions({
  cardStatus,
  updatingStatus,
  cardDetailsVisible,
  onShowDetails,
  onHideDetails,
  onToggleStatus,
  onOrderCard,
}: CardActionsProps) {
  return (
    <div className="card-actions">
      <button
        type="button"
        className="card-btn primary"
        onClick={cardDetailsVisible ? onHideDetails : onShowDetails}
      >
        {cardDetailsVisible ? "Hide" : "Show card details"}
      </button>

      <button
        type="button"
        className={
          cardStatus === "FROZEN" ? "card-btn unfreeze" : "card-btn freeze"
        }
        onClick={onToggleStatus}
        disabled={updatingStatus}
      >
        <Snowflake size={16} />

        {updatingStatus
          ? "Updating..."
          : cardStatus === "FROZEN"
            ? "Unfreeze card"
            : "Freeze card"}
      </button>

      <button type="button" className="card-btn danger" onClick={onOrderCard}>
        Order new card
      </button>
    </div>
  );
}
