import { useState, type SubmitEvent } from "react";
import { Link, useNavigate } from "react-router";

import { applyForLoan } from "../api/loanClient";

import "../styles/loan-application.css";

export default function LoanApplicationPage() {
  const navigate = useNavigate();

  const [loanType, setLoanType] = useState("");
  const [loanAmount, setLoanAmount] = useState("");
  const [monthlyIncome, setMonthlyIncome] = useState("");
  const [monthlyExpenses, setMonthlyExpenses] = useState("");
  const [duration, setDuration] = useState("12");

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(
    event: SubmitEvent<HTMLFormElement>,
  ): Promise<void> {
    event.preventDefault();

    setError(null);

    const amount = Number(loanAmount);
    const income = Number(monthlyIncome);
    const expenses = Number(monthlyExpenses);
    const months = Number(duration);

    if (amount <= 0) {
      setError("Please enter a valid loan amount.");
      return;
    }

    if (income <= 0) {
      setError("Please enter a valid monthly income.");
      return;
    }

    if (expenses < 0) {
      setError("Monthly expenses cannot be negative.");
      return;
    }

    if (months <= 0 || months % 6 !== 0) {
      setError("Loan duration must be a multiple of 6 months.");
      return;
    }

    try {
      setSubmitting(true);

      const response = await applyForLoan({
        loan_type: loanType,
        loan_amount: amount,
        monthly_income: income,
        monthly_expenses: expenses,
        duration: months,
      });

      if (!response.eligible) {
        setError(
          "Unfortunately, you are not currently eligible for this loan.",
        );
        return;
      }

      navigate("/my-loans");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to submit loan application.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="loan-application-page">
      <header className="customer-header">
        <div className="customer-brand-lockup">
          <span className="auth-brand-mark" aria-hidden="true">
            D
          </span>
          <span>Demo Bank</span>
        </div>

        <Link to="/my-loans" className="customer-back">
          Back to loans
        </Link>
      </header>

      <main className="loan-application-container">
        <header className="loan-application-header">
          <p className="auth-eyebrow">Customer Loans</p>
          <h1>Apply for a loan</h1>
          <p className="loan-application-subtitle">
            Tell us about the loan you are looking for and your current
            financial situation.
          </p>
        </header>

        <section className="loan-application-card">
          <form
            className="loan-application-form"
            onSubmit={handleSubmit}
            aria-busy={submitting}
          >
            <div className="loan-application-field">
              <label htmlFor="loan-type">Loan type</label>

              <input
                id="loan-type"
                value={loanType}
                onChange={(event) => setLoanType(event.target.value)}
                disabled={submitting}
                required
              />
            </div>

            <div className="loan-application-field">
              <label htmlFor="loan-amount">Loan amount</label>

              <div className="loan-application-input-wrapper">
                <span>£</span>

                <input
                  id="loan-amount"
                  type="number"
                  min="1"
                  step="1"
                  value={loanAmount}
                  onChange={(event) => setLoanAmount(event.target.value)}
                  placeholder="5000"
                  disabled={submitting}
                  required
                />
              </div>
            </div>

            <div className="loan-application-field">
              <label htmlFor="monthly-income">Monthly income</label>

              <div className="loan-application-input-wrapper">
                <span>£</span>

                <input
                  id="monthly-income"
                  type="number"
                  min="0"
                  step="1"
                  value={monthlyIncome}
                  onChange={(event) => setMonthlyIncome(event.target.value)}
                  placeholder="3000"
                  disabled={submitting}
                  required
                />
              </div>
            </div>

            <div className="loan-application-field">
              <label htmlFor="monthly-expenses">Monthly expenses</label>

              <div className="loan-application-input-wrapper">
                <span>£</span>

                <input
                  id="monthly-expenses"
                  type="number"
                  min="0"
                  step="1"
                  value={monthlyExpenses}
                  onChange={(event) => setMonthlyExpenses(event.target.value)}
                  placeholder="1500"
                  disabled={submitting}
                  required
                />
              </div>
            </div>

            <div className="loan-application-field">
              <label htmlFor="duration">Loan duration (Months)</label>

              <input
                id="duration"
                value={duration}
                onChange={(event) => setDuration(event.target.value)}
                disabled={submitting}
                required
              />
              <p className="loan-application-help">
                Loan duration must be in multiples of 6 months.
              </p>
            </div>

            {error && (
              <p className="loan-application-error" role="alert">
                {error}
              </p>
            )}

            <button
              type="submit"
              className="loan-application-button"
              disabled={submitting}
            >
              {submitting ? "Submitting..." : "Submit application"}
            </button>
          </form>
        </section>
      </main>
    </div>
  );
}
