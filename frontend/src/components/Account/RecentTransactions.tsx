import { Link } from "react-router";

import { useTransactions } from "../../hooks/useTransactions";
import { routes } from "../../routes";
import type { TransactionType } from "../../types/transaction";

function formatType(type: TransactionType) {
  return type[0] + type.slice(1).toLowerCase();
}

export default function RecentTransactions() {
  const { data, isLoading, isError } = useTransactions({ limit: 3 });
  const transactions = data?.items ?? [];

  if (isLoading) {
    return (
      <section className="customer-recent">
        <div className="customer-recent-header">
          <h2>Recent transactions</h2>
        </div>
        <p className="customer-recent-empty">Loading transactions…</p>
      </section>
    );
  }

  if (isError) {
    return (
      <section className="customer-recent">
        <div className="customer-recent-header">
          <h2>Recent transactions</h2>
        </div>
        <p className="customer-recent-empty">
          Couldn't load your recent transactions.
        </p>
      </section>
    );
  }

  if (transactions.length === 0) {
    return (
      <section className="customer-recent">
        <div className="customer-recent-header">
          <h2>Recent transactions</h2>
        </div>
        <p className="customer-recent-empty">No transactions yet.</p>
      </section>
    );
  }

  return (
    <section className="customer-recent">
      <div className="customer-recent-header">
        <h2>Recent transactions</h2>
        <Link to={routes.transactionHistory} className="customer-recent-link">
          View all
        </Link>
      </div>

      <div className="transaction-history-list">
        {transactions.map((transaction) => (
          <div className="history-row" key={transaction.id}>
            <span>
              <strong>{formatType(transaction.transaction_type)}</strong>
              <small>{new Date(transaction.created_at).toLocaleString()}</small>
            </span>
            <span className="history-reference">
              {transaction.reference.slice(0, 10)}
            </span>
            <span
              className={
                transaction.direction === "CREDIT"
                  ? "history-amount history-credit"
                  : "history-amount"
              }
            >
              {transaction.direction === "CREDIT" ? "+" : "-"}£
              {transaction.amount}
            </span>
            <span
              className={`history-status history-status-${transaction.status.toLowerCase()}`}
            >
              {transaction.status}
            </span>
          </div>
        ))}
      </div>
    </section>
  );
}
