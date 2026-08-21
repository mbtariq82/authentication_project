import { useEffect, useState, type SubmitEvent } from "react";
import { Link, useNavigate, useLocation } from "react-router";

import { getUserLoans, repayLoan, type Loan } from "../api/loanClient";
import LoanNavigation from "../components/LoanNavigation";

import "../styles/loan-repayment.css";

export default function LoanRepaymentPage() {
  const location = useLocation();
  const loanId = location.state?.loanId;
  const navigate = useNavigate();

  const [loan, setLoan] = useState<Loan | null>(null);
  const [amount, setAmount] = useState("");

  const [loading, setLoading] = useState(true);
  const [repaying, setRepaying] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [showWarning, setShowWarning] = useState(false);
  const [showOverpaymentWarning, setShowOverpaymentWarning] = useState(false);

  useEffect(() => {
    const loadLoan = async () => {
      try {
        const response = await getUserLoans();

        const selectedLoan = response.loans.find(
          (loan) => loan.id === Number(loanId),
        );

        if (!selectedLoan) {
          setError("Loan not found.");
          return;
        }

        if (selectedLoan.current_loan_status !== "ACCEPTED") {
          setError("This loan is not currently available for repayment.");
          return;
        }

        setLoan(selectedLoan);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load loan.");
      } finally {
        setLoading(false);
      }
    };

    loadLoan();
  }, [loanId]);

  async function submitRepayment() {
    if (!loan) {
      return;
    }

    const repaymentAmount = Number(amount);

    try {
      setRepaying(true);
      setError(null);

      await repayLoan({
        loan_id: loan.id,
        amount: repaymentAmount,
      });

      navigate("/my-loans");
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to make repayment.",
      );
    } finally {
      setRepaying(false);
    }
  }

  function handleRepayment(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!loan) {
      return;
    }

    const repaymentAmount = Number(amount);

    if (!repaymentAmount || repaymentAmount <= 0) {
      setError("Please enter a valid repayment amount.");
      return;
    }

    if (repaymentAmount > loan.loan_amount) {
      setError(
        "Repayment amount cannot be greater than the remaining loan amount.",
      );
      return;
    }

    if (repaymentAmount < loan.emi) {
      setShowWarning(true);
      return;
    }

    if (repaymentAmount > loan.emi) {
      setShowOverpaymentWarning(true);
      return;
    }

    // Exactly the EMI.
    void submitRepayment();
  }

  async function acknowledgeAndRepay(
    warningType: "underpayment" | "overpayment",
  ) {
    if (warningType === "underpayment") {
      setShowWarning(false);
    } else {
      setShowOverpaymentWarning(false);
    }

    await submitRepayment();
  }

  if (loading) {
    return (
      <div className="loan-repayment-page">
        <div className="loan-repayment-container">
          <div className="loan-repayment-loading">Loading loan...</div>
        </div>
      </div>
    );
  }

  if (!loan) {
    return (
      <div className="loan-repayment-page">
        <div className="loan-repayment-container">
          <div className="loan-repayment-error">
            {error ?? "Loan not found."}
          </div>

          <Link to="/my-loans" className="loan-repayment-back">
            Back to loans
          </Link>
        </div>
      </div>
    );
  }

  const currencyFormatter = new Intl.NumberFormat("en-GB", {
    style: "currency",
    currency: "GBP",
  });

  const formattedAmount = currencyFormatter.format(loan.loan_amount);
  const formattedEmi = currencyFormatter.format(loan.emi);

  return (
    <div className="loan-repayment-page">
      <LoanNavigation showBackToLoans />

      <main className="loan-repayment-container">
        <header className="loan-repayment-header">
          <p className="auth-eyebrow">Loan Repayment</p>
          <h1>Make a repayment</h1>
          <p>Enter the amount you would like to repay towards your loan.</p>
        </header>

        <section className="loan-repayment-card">
          <div className="loan-repayment-summary">
            <div>
              <span className="loan-repayment-label">Loan type</span>
              <span className="loan-repayment-value">{loan.loan_type}</span>
            </div>

            <div>
              <span className="loan-repayment-label">Remaining amount</span>
              <span className="loan-repayment-value">{formattedAmount}</span>
            </div>

            <div>
              <span className="loan-repayment-label">Monthly repayment</span>
              <span className="loan-repayment-value">{formattedEmi}</span>
            </div>

            <div>
              <span className="loan-repayment-label">Interest rate</span>
              <span className="loan-repayment-value">{loan.interest}%</span>
            </div>

            <div>
              <span className="loan-repayment-label">Duration</span>
              <span className="loan-repayment-value">
                {loan.duration} months
              </span>
            </div>
          </div>

          <form className="loan-repayment-form" onSubmit={handleRepayment}>
            <div className="loan-repayment-field">
              <label htmlFor="repayment-amount">Repayment amount</label>

              <div className="loan-repayment-input-wrapper">
                <span>£</span>

                <input
                  id="repayment-amount"
                  type="number"
                  min="0.01"
                  step="0.01"
                  value={amount}
                  onChange={(event) => setAmount(event.target.value)}
                  placeholder="0.00"
                  required
                  disabled={repaying}
                />
              </div>
            </div>

            {error && (
              <p className="loan-repayment-error" role="alert">
                {error}
              </p>
            )}

            <button
              type="submit"
              className="loan-repayment-button"
              disabled={repaying}
            >
              {repaying ? "Processing..." : "Make repayment"}
            </button>
          </form>
        </section>
      </main>

      {/* Underpayment warning */}
      {showWarning && (
        <div className="loan-repayment-modal-backdrop" role="presentation">
          <div
            className="loan-repayment-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="repayment-warning-title"
          >
            <h2 id="repayment-warning-title">Repayment below monthly amount</h2>

            <p>
              The amount you have entered is less than your expected monthly
              repayment of <strong>{formattedEmi}</strong>.
            </p>

            <p>
              Making a repayment below your expected monthly amount may increase
              the remaining duration of your loan and could result in you paying
              more interest over the life of the loan.
            </p>

            <p>Are you sure you want to continue with this repayment?</p>

            <div className="loan-repayment-modal-actions">
              <button
                type="button"
                className="loan-repayment-modal-cancel"
                onClick={() => setShowWarning(false)}
                disabled={repaying}
              >
                Cancel
              </button>

              <button
                type="button"
                className="loan-repayment-modal-confirm"
                onClick={() => void acknowledgeAndRepay("underpayment")}
                disabled={repaying}
              >
                {repaying ? "Processing..." : "Acknowledge & make payment"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Overpayment warning */}
      {showOverpaymentWarning && (
        <div className="loan-repayment-modal-backdrop" role="presentation">
          <div
            className="loan-repayment-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="overpayment-warning-title"
          >
            <h2 id="overpayment-warning-title">Larger repayment</h2>

            <p>
              You are paying more than your expected monthly repayment of{" "}
              <strong>{formattedEmi}</strong>.
            </p>

            <p>
              This additional repayment will reduce the remaining balance of
              your loan and shorten the remaining loan duration.
            </p>

            <p>
              Your monthly repayment amount will remain the same, allowing you
              to pay off the loan sooner.
            </p>

            <p>Would you like to continue with this repayment?</p>

            <div className="loan-repayment-modal-actions">
              <button
                type="button"
                className="loan-repayment-modal-cancel"
                onClick={() => setShowOverpaymentWarning(false)}
                disabled={repaying}
              >
                Cancel
              </button>

              <button
                type="button"
                className="loan-repayment-modal-confirm"
                onClick={() => void acknowledgeAndRepay("overpayment")}
                disabled={repaying}
              >
                {repaying ? "Processing..." : "Acknowledge & make payment"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
