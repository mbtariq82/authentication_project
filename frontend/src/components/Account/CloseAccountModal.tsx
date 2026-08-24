type CloseAccountModalProps = {
  reason: string;
  closing: boolean;
  error: string | null;
  onReasonChange: (reason: string) => void;
  onConfirm: () => void;
  onClose: () => void;
};

export default function CloseAccountModal({
  reason,
  closing,
  error,
  onReasonChange,
  onConfirm,
  onClose,
}: CloseAccountModalProps) {
  const trimmedReason = reason.trim();

  return (
    <div className="card-modal-overlay">
      <div className="card-modal">
        <h2>Close your account?</h2>

        <p>
          This will close your account. Your balance must be zero before you can
          close it. Please contact the bank if you need to reopen it later.
        </p>

        <input
          type="text"
          value={reason}
          onChange={(event) => onReasonChange(event.target.value)}
          placeholder="Reason (required)"
          autoFocus
        />

        {error && <div className="card-error">{error}</div>}

        <div className="card-modal-actions">
          <button
            type="button"
            className="card-btn"
            onClick={onClose}
            disabled={closing}
          >
            Cancel
          </button>

          <button
            type="button"
            className="card-btn danger"
            onClick={onConfirm}
            disabled={closing || trimmedReason.length === 0}
          >
            {closing ? "Closing..." : "Close account"}
          </button>
        </div>
      </div>
    </div>
  );
}
