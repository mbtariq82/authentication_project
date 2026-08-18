import { useEffect, useState, type SubmitEvent } from "react";
import { Link, useNavigate, useParams } from "react-router";

import { getUserLoans, repayLoan, type Loan } from "../api/loanClient";

import "../styles/loan-repayment.css";

export default function LoanRepaymentPage() {
  const { loanId } = useParams();
  const navigate = useNavigate();

  const [loan, setLoan] = useState<Loan | null>(null);
  const [amount, setAmount] = useState("");

  const [loading, setLoading] = useState(true);
  const [repaying, setRepaying] = useState(false);
  const [error, setError] = useState<string | null>(null);

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

  async function handleRepayment(event: SubmitEvent<HTMLFormElement>) {
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

    try {
      setRepaying(true);
      setError(null);

      await repayLoan(loan.id, repaymentAmount);

      navigate("/loans");
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to make repayment.",
      );
    } finally {
      setRepaying(false);
    }
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

          <Link to="/loans" className="loan-repayment-back">
            Back to loans
          </Link>
        </div>
      </div>
    );
  }

  const formattedAmount = new Intl.NumberFormat("en-GB", {
    style: "currency",
    currency: "GBP",
  }).format(loan.loan_amount);

  return (
    <div className="loan-repayment-page">
      <header className="customer-header">
        <div className="customer-brand-lockup">
          <span className="auth-brand-mark" aria-hidden="true">
            D
          </span>
          <span>Demo Bank</span>
        </div>

        <Link to="/loans" className="customer-back">
          Back to loans
        </Link>
      </header>

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
              <span className="loan-repayment-label">Remaining balance</span>

              <span className="loan-repayment-value">{formattedAmount}</span>
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
    </div>
  );
}
