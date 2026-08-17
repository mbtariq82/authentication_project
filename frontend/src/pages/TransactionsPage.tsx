import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router";

import { logout } from "../api/authClient";
import { clearTokens } from "../auth/tokenStorage";
import { useAccount } from "../hooks/useAccount";
import { useBeneficiaries } from "../hooks/useBeneficiaries";
import { useCreateTransaction } from "../hooks/useTransactions";
import type {
  TransactionDirection,
  TransactionType,
} from "../types/transaction";

const transactionTypes: TransactionType[] = [
  "DEPOSIT",
  "WITHDRAWAL",
  "TRANSFER",
];

export default function TransactionsPage() {
  const navigate = useNavigate();
  const accountQuery = useAccount();
  const beneficiariesQuery = useBeneficiaries();
  const createMutation = useCreateTransaction();
  const [type, setType] = useState<TransactionType>("DEPOSIT");
  const [amount, setAmount] = useState("");
  const [beneficiaryId, setBeneficiaryId] = useState("");
  const [description, setDescription] = useState("");
  const [message, setMessage] = useState("");

  async function handleLogout() {
    try {
      await logout();
    } finally {
      clearTokens();
      navigate("/login", { replace: true });
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!accountQuery.data) return;
    setMessage("");
    const direction: TransactionDirection =
      type === "DEPOSIT" ? "CREDIT" : "DEBIT";
    try {
      await createMutation.mutateAsync({
        account_id: accountQuery.data.id,
        beneficiary_id: type === "TRANSFER" ? Number(beneficiaryId) : null,
        transaction_type: type,
        direction,
        amount,
        description: description || null,
      });
      setMessage(
        type === "TRANSFER"
          ? "Transfer submitted and is awaiting processing."
          : `${type[0]}${type.slice(1).toLowerCase()} completed successfully.`,
      );
      setAmount("");
      setBeneficiaryId("");
      setDescription("");
    } catch (error) {
      setMessage(
        error instanceof Error ? error.message : "Transaction failed.",
      );
    }
  }

  const isLoading = accountQuery.isLoading || beneficiariesQuery.isLoading;
  const accountError = accountQuery.error?.message;
  const isTransfer = type === "TRANSFER";

  return (
    <main className="customer-home">
      <header className="customer-header">
        <Link className="customer-brand-lockup" to="/account">
          <span className="auth-brand-mark" aria-hidden="true">
            D
          </span>
          <span>Demo Bank</span>
        </Link>
        <nav className="customer-nav" aria-label="Customer navigation">
          <Link to="/account">Account</Link>
          <Link to="/beneficiaries">Beneficiaries</Link>
          <Link className="customer-nav-active" to="/transactions">
            Transactions
          </Link>
          <button
            className="customer-logout"
            type="button"
            onClick={handleLogout}
          >
            Sign out
          </button>
        </nav>
      </header>

      <section className="customer-content transactions-page">
        <div className="customer-welcome">
          <p className="auth-eyebrow">Payments</p>
          <h1>Move money</h1>
          <p>
            Make a demo deposit, withdrawal, or transfer from your everyday
            account.
          </p>
        </div>

        <div className="transaction-account-banner">
          <div>
            <p className="customer-card-label">Everyday account</p>
            <strong>
              {accountQuery.data
                ? `Account #${accountQuery.data.id}`
                : "Account unavailable"}
            </strong>
          </div>
          <span className="transaction-balance">
            {accountQuery.data ? `Balance £${accountQuery.data.balance}` : ""}
          </span>
        </div>

        {isLoading && <p role="status">Loading account details...</p>}
        {accountError && <p className="transaction-error">{accountError}</p>}

        {!isLoading && !accountError && (
          <section
            className="transaction-panel"
            aria-labelledby="transaction-form-title"
          >
            <div
              className="transaction-type-tabs"
              role="tablist"
              aria-label="Transaction type"
            >
              {transactionTypes.map((option) => (
                <button
                  key={option}
                  className={
                    type === option
                      ? "transaction-tab-active"
                      : "transaction-tab"
                  }
                  type="button"
                  role="tab"
                  aria-selected={type === option}
                  onClick={() => setType(option)}
                >
                  {option[0]}
                  {option.slice(1).toLowerCase()}
                </button>
              ))}
            </div>

            <form className="transaction-form" onSubmit={handleSubmit}>
              <h2 id="transaction-form-title">
                {isTransfer
                  ? "Send a transfer"
                  : `${type[0]}${type.slice(1).toLowerCase()} funds`}
              </h2>
              <label>
                Amount
                <input
                  type="number"
                  min="0.01"
                  step="0.01"
                  value={amount}
                  onChange={(event) => setAmount(event.target.value)}
                  required
                />
              </label>
              {isTransfer && (
                <label>
                  Beneficiary
                  <select
                    value={beneficiaryId}
                    onChange={(event) => setBeneficiaryId(event.target.value)}
                    required
                  >
                    <option value="">Select a beneficiary</option>
                    {beneficiariesQuery.data?.map((beneficiary) => (
                      <option key={beneficiary.id} value={beneficiary.id}>
                        {beneficiary.name} · {beneficiary.bank_name}
                      </option>
                    ))}
                  </select>
                </label>
              )}
              <label>
                Description
                <input
                  maxLength={255}
                  value={description}
                  onChange={(event) => setDescription(event.target.value)}
                  placeholder="Optional"
                />
              </label>
              {message && (
                <p className="transaction-message" role="status">
                  {message}
                </p>
              )}
              <button
                className="auth-primary-action"
                type="submit"
                disabled={
                  createMutation.isPending ||
                  (isTransfer && !beneficiariesQuery.data?.length)
                }
              >
                {createMutation.isPending
                  ? "Submitting..."
                  : isTransfer
                    ? "Submit transfer"
                    : `Complete ${type.toLowerCase()}`}
              </button>
            </form>
          </section>
        )}
      </section>
    </main>
  );
}
