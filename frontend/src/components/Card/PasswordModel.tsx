type PasswordModalProps = {
  password: string;
  passwordError: string | null;
  unmasking: boolean;
  onPasswordChange: (password: string) => void;
  onConfirm: () => void;
  onClose: () => void;
};

export default function PasswordModal({
  password,
  passwordError,
  unmasking,
  onPasswordChange,
  onConfirm,
  onClose,
}: PasswordModalProps) {
  return (
    <div className="card-modal-overlay">
      <div className="card-modal">
        <h2>Enter your password</h2>

        <p>Enter your password to view your full card details.</p>

        <input
          type="password"
          value={password}
          onChange={(event) => onPasswordChange(event.target.value)}
          placeholder="Password"
          autoFocus
        />

        {passwordError && <div className="card-error">{passwordError}</div>}

        <div className="card-modal-actions">
          <button type="button" className="card-btn" onClick={onClose}>
            Cancel
          </button>

          <button
            type="button"
            className="card-btn primary"
            onClick={onConfirm}
            disabled={unmasking}
          >
            {unmasking ? "Verifying..." : "Confirm"}
          </button>
        </div>
      </div>
    </div>
  );
}
