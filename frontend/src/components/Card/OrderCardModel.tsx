type OrderCardModalProps = {
  ordering: boolean;
  onConfirm: () => void;
  onClose: () => void;
};

export default function OrderCardModal({
  ordering,
  onConfirm,
  onClose,
}: OrderCardModalProps) {
  return (
    <div className="card-modal-overlay">
      <div className="card-modal">
        <h2>Order a new card?</h2>

        <p>
          Only use this option if your current card has been lost or stolen.
          Your current card will be cancelled and a new card will be issued.
        </p>

        <div className="card-modal-actions">
          <button
            type="button"
            className="card-btn"
            onClick={onClose}
            disabled={ordering}
          >
            Cancel
          </button>

          <button
            type="button"
            className="card-btn danger"
            onClick={onConfirm}
            disabled={ordering}
          >
            {ordering ? "Ordering..." : "Order new card"}
          </button>
        </div>
      </div>
    </div>
  );
}
