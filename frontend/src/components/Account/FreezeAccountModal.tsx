type FreezeAccountModalProps = {
  freezing: boolean;
  error: string | null;
  onConfirm: () => void;
  onClose: () => void;
};

export default function FreezeAccountModal({
  freezing,
  error,
  onConfirm,
  onClose,
}: FreezeAccountModalProps) {
  return (
    <div className="card-modal-overlay">
      <div className="card-modal">
        <h2>Freeze your account?</h2>

        <p>
          While frozen, you won't be able to make transfers. You can unfreeze
          your account again at any time.
        </p>

        {error && <div className="card-error">{error}</div>}

        <div className="card-modal-actions">
          <button
            type="button"
            className="card-btn"
            onClick={onClose}
            disabled={freezing}
          >
            Cancel
          </button>

          <button
            type="button"
            className="card-btn danger"
            onClick={onConfirm}
            disabled={freezing}
          >
            {freezing ? "Freezing..." : "Freeze account"}
          </button>
        </div>
      </div>
    </div>
  );
}
