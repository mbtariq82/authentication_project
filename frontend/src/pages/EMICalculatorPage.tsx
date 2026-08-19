import { useMemo, useState } from "react";
import { Link } from "react-router";

import "../styles/emi-calculator.css";

const LOAN_INTEREST_RATES: Record<string, number> = {
  House: 5,
  Automobile: 6,
  Education: 4,
  "Emergency Expense": 8,
};

export default function EMICalculatorPage() {
  const [loanType, setLoanType] = useState("");
  const [loanAmount, setLoanAmount] = useState("");
  const [duration, setDuration] = useState("");

  const calculation = useMemo(() => {
    const principal = Number(loanAmount);
    const months = Number(duration);
    const annualRate = LOAN_INTEREST_RATES[loanType];

    if (
      !loanType ||
      !principal ||
      principal <= 0 ||
      annualRate === undefined ||
      !months ||
      months <= 0
    ) {
      return null;
    }

    const monthlyRate = annualRate / 100 / 12;

    const emi =
      monthlyRate === 0
        ? principal / months
        : (principal * monthlyRate * Math.pow(1 + monthlyRate, months)) /
          (Math.pow(1 + monthlyRate, months) - 1);

    const totalRepayment = emi * months;
    const totalInterest = totalRepayment - principal;

    return {
      emi,
      totalRepayment,
      totalInterest,
      annualRate,
    };
  }, [loanType, loanAmount, duration]);

  const formatCurrency = (value: number) =>
    new Intl.NumberFormat("en-GB", {
      style: "currency",
      currency: "GBP",
    }).format(value);

  return (
    <div className="emi-calculator-page">
      <header className="customer-header">
        <div className="customer-brand-lockup">
          <span className="auth-brand-mark" aria-hidden="true">
            D
          </span>
          <span>Demo Bank</span>
        </div>

        <div className="customer-header-actions">
          <Link to="/loans/apply" className="customer-apply-loan">
            Apply for a loan
          </Link>

          <Link to="/account" className="customer-back">
            Back to account
          </Link>
        </div>
      </header>

      <main className="emi-calculator-container">
        <header className="emi-calculator-header">
          <p className="auth-eyebrow">Loan Calculator</p>
          <h1>EMI Calculator</h1>
          <p className="emi-calculator-subtitle">
            Estimate your monthly loan repayment before applying.
          </p>
        </header>

        <div className="emi-calculator-layout">
          <section className="emi-calculator-card">
            <h2>Loan details</h2>

            <div className="emi-calculator-form">
              <div className="emi-field">
                <label htmlFor="loan-type">Loan type</label>

                <select
                  id="loan-type"
                  value={loanType}
                  onChange={(event) => setLoanType(event.target.value)}
                >
                  <option value="" disabled>
                    Select a loan type
                  </option>
                  <option value="House">House</option>
                  <option value="Automobile">Automobile</option>
                  <option value="Education">Education</option>
                  <option value="Emergency Expense">Emergency Expense</option>
                </select>
              </div>

              <div className="emi-field">
                <label htmlFor="loan-amount">Loan amount</label>

                <div className="emi-input-wrapper">
                  <span>£</span>

                  <input
                    id="loan-amount"
                    type="number"
                    min="1"
                    step="1"
                    value={loanAmount}
                    onChange={(event) => setLoanAmount(event.target.value)}
                    placeholder="10000"
                  />
                </div>
              </div>

              <div className="emi-field">
                <label htmlFor="interest-rate">Annual interest rate</label>

                <div className="emi-input-wrapper">
                  <input
                    id="interest-rate"
                    type="text"
                    value={loanType ? `${LOAN_INTEREST_RATES[loanType]}%` : ""}
                    placeholder="Select a loan type"
                    readOnly
                  />
                </div>
              </div>

              <div className="emi-field">
                <label htmlFor="duration">Loan duration (Months)</label>

                <input
                  id="duration"
                  value={duration}
                  onChange={(event) => setDuration(event.target.value)}
                />

                <p className="loan-application-help">
                  Loan duration must be in multiples of 6 months.
                </p>
              </div>
            </div>
          </section>

          <section className="emi-result-card">
            <p className="emi-result-label">Estimated monthly payment</p>

            <div className="emi-result-value">
              {calculation ? formatCurrency(calculation.emi) : "£0.00"}
            </div>

            <div className="emi-result-details">
              <div className="emi-result-row">
                <span>Loan amount</span>
                <strong>
                  {calculation ? formatCurrency(Number(loanAmount)) : "£0.00"}
                </strong>
              </div>

              <div className="emi-result-row">
                <span>Interest rate</span>
                <strong>
                  {calculation ? `${calculation.annualRate}%` : "0%"}
                </strong>
              </div>

              <div className="emi-result-row">
                <span>Total interest</span>
                <strong>
                  {calculation
                    ? formatCurrency(calculation.totalInterest)
                    : "£0.00"}
                </strong>
              </div>

              <div className="emi-result-row">
                <span>Total repayment</span>
                <strong>
                  {calculation
                    ? formatCurrency(calculation.totalRepayment)
                    : "£0.00"}
                </strong>
              </div>

              <div className="emi-result-row">
                <span>Duration</span>
                <strong>{duration || "0"} months</strong>
              </div>
            </div>

            <Link to="/loans/apply" className="emi-apply-button">
              Apply for a loan
            </Link>
          </section>
        </div>
      </main>
    </div>
  );
}
