import { useEffect, useState } from "react";
import { Link } from "react-router";

import { getUserLoans, type Loan } from "../api/loanClient";

import "../styles/loan-page.css";

export default function LoansPage() {
  const [loans, setLoans] = useState<Loan[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadLoans = async () => {
      try {
        const response = await getUserLoans();
        setLoans(response.loans);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load loans.");
      } finally {
        setLoading(false);
      }
    };

    loadLoans();
  }, []);

  if (loading) {
    return (
      <div className="loans-page">
        <div className="loans-page-container">
          <div className="loans-loading">Loading loans...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="loans-page">
      <header className="customer-header">
        <div className="customer-brand-lockup">
          <span className="auth-brand-mark" aria-hidden="true">
            D
          </span>
          <span>Demo Bank</span>
        </div>

        <Link to="/account" className="customer-back">
          Back to account
        </Link>
      </header>

      <main className="loans-page-container">
        <header className="loans-page-header">
          <p className="auth-eyebrow">Customer Loans</p>
          <h1>My Loans</h1>
          <p className="loans-page-subtitle">
            View and manage your current loans.
          </p>
        </header>

        {error && <div className="loans-error">{error}</div>}

        {!error && loans.length === 0 && (
          <div className="loan-empty-card">
            <h2>No current loans</h2>
            <p>You don't currently have any active or pending loans.</p>

            <Link to="/loans/apply" className="loan-action-button">
              Apply for a loan
            </Link>
          </div>
        )}

        {!error && loans.length > 0 && (
          <div className="loan-list">
            {loans.map((loan) => (
              <LoanCard key={loan.id} loan={loan} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

type LoanCardProps = {
  loan: Loan;
};

function LoanCard({ loan }: LoanCardProps) {
  const formattedAmount = new Intl.NumberFormat("en-GB", {
    style: "currency",
    currency: "GBP",
  }).format(loan.loan_amount);

  return (
    <article className="loan-card">
      <div className="loan-card-header">
        <div>
          <p className="loan-card-label">Loan</p>
          <h2>{loan.loan_type}</h2>
        </div>

        <span
          className={`loan-status ${loan.current_loan_status.toLowerCase()}`}
        >
          {loan.current_loan_status}
        </span>
      </div>

      <div className="loan-card-details">
        <div className="loan-detail">
          <span className="loan-detail-label">Amount</span>
          <span className="loan-detail-value">{formattedAmount}</span>
        </div>

        <div className="loan-detail">
          <span className="loan-detail-label">Duration</span>
          <span className="loan-detail-value">{loan.duration} months</span>
        </div>
      </div>

      {loan.current_loan_status === "ACCEPTED" && (
        <div className="loan-card-actions">
          <Link
            to={`/repay`}
            state={{ loanId: loan.id }}
            className="loan-action-button"
          >
            Make repayment
          </Link>
        </div>
      )}
    </article>
  );
}
