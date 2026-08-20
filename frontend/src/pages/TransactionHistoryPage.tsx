import { useState } from "react";

import CustomerNavigation from "../components/CustomerNavigation";
import {
  useCancelTransaction,
  useTransaction,
  useTransactionLogs,
  useTransactions,
} from "../hooks/useTransactions";
import type {
  TransactionFilters,
  TransactionStatus,
  TransactionType,
} from "../types/transaction";

const pageSize = 10;

function formatType(type: TransactionType) {
  return type[0] + type.slice(1).toLowerCase();
}

export default function TransactionHistoryPage() {
  const [status, setStatus] = useState<TransactionStatus | "">("");
  const [type, setType] = useState<TransactionType | "">("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [offset, setOffset] = useState(0);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [message, setMessage] = useState("");

  const filters: TransactionFilters = {
    ...(status ? { status } : {}),
    ...(type ? { transaction_type: type } : {}),
    ...(startDate ? { created_from: `${startDate}T00:00` } : {}),
    ...(endDate ? { created_to: `${endDate}T23:59:59` } : {}),
    offset,
    limit: pageSize,
  };
  const transactionsQuery = useTransactions(filters);
  const selectedQuery = useTransaction(selectedId);
  const logsQuery = useTransactionLogs(selectedId);
  const cancelMutation = useCancelTransaction();

  function resetFilters() {
    setStatus("");
    setType("");
    setStartDate("");
    setEndDate("");
    setOffset(0);
    setSelectedId(null);
  }

  async function cancelSelected() {
    if (!selectedId) return;
    setMessage("");
    try {
      await cancelMutation.mutateAsync(selectedId);
      setMessage("Transaction cancelled.");
    } catch (error) {
      setMessage(
        error instanceof Error
          ? error.message
          : "Unable to cancel transaction.",
      );
    }
  }

  const page = transactionsQuery.data;
  const canGoBack = offset > 0;
  const canGoNext = Boolean(page && offset + page.items.length < page.total);

  return (
    <main className="customer-home">
      <CustomerNavigation />

      <section className="customer-content transactions-page">
        <div className="customer-welcome">
          <h1>Transaction history</h1>
          <p>Review your account activity and transaction audit trail.</p>
        </div>

        <section
          className="transaction-panel history-panel"
          aria-labelledby="history-title"
        >
          <div className="history-toolbar">
            <div>
              <h2 id="history-title">Transactions</h2>
            </div>
            <div className="history-filters">
              <div className="history-range-filter">
                <input
                  aria-label="Start date"
                  type="date"
                  value={startDate}
                  max={endDate || undefined}
                  onChange={(event) => {
                    setStartDate(event.target.value);
                    setOffset(0);
                    setSelectedId(null);
                  }}
                />
                <span aria-hidden="true">to</span>
                <input
                  aria-label="End date"
                  type="date"
                  value={endDate}
                  min={startDate || undefined}
                  onChange={(event) => {
                    setEndDate(event.target.value);
                    setOffset(0);
                    setSelectedId(null);
                  }}
                />
              </div>
              <select
                aria-label="Filter by type"
                value={type}
                onChange={(event) => {
                  setType(event.target.value as TransactionType | "");
                  setOffset(0);
                }}
              >
                <option value="">All types</option>
                <option value="DEPOSIT">Deposits</option>
                <option value="WITHDRAWAL">Withdrawals</option>
                <option value="TRANSFER">Transfers</option>
              </select>
              <select
                aria-label="Filter by status"
                value={status}
                onChange={(event) => {
                  setStatus(event.target.value as TransactionStatus | "");
                  setOffset(0);
                }}
              >
                <option value="">All statuses</option>
                <option value="PENDING">Pending</option>
                <option value="COMPLETED">Completed</option>
                <option value="FAILED">Failed</option>
                <option value="CANCELLED">Cancelled</option>
              </select>
              <button
                className="secondary-action"
                type="button"
                onClick={resetFilters}
              >
                Reset
              </button>
            </div>
          </div>

          {transactionsQuery.isLoading && (
            <p role="status">Loading transactions...</p>
          )}
          {transactionsQuery.isError && (
            <p className="transaction-error">
              {transactionsQuery.error.message}
            </p>
          )}
          {!transactionsQuery.isLoading &&
            !transactionsQuery.isError &&
            page?.items.length === 0 && (
              <p className="beneficiary-empty">
                No transactions match these filters.
              </p>
            )}

          {page && page.items.length > 0 && (
            <div className="transaction-history-list">
              {page.items.map((transaction) => (
                <button
                  className={
                    selectedId === transaction.id
                      ? "history-row history-row-selected"
                      : "history-row"
                  }
                  type="button"
                  key={transaction.id}
                  onClick={() => {
                    setSelectedId(transaction.id);
                    setMessage("");
                  }}
                >
                  <span>
                    <strong>{formatType(transaction.transaction_type)}</strong>
                    <small>
                      {new Date(transaction.created_at).toLocaleString()}
                    </small>
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
                </button>
              ))}
            </div>
          )}

          <div className="history-pagination">
            <button
              className="secondary-action"
              type="button"
              disabled={!canGoBack}
              onClick={() => setOffset(Math.max(0, offset - pageSize))}
            >
              Previous
            </button>
            <span>
              {page
                ? `${Math.min(offset + 1, page.total)}-${Math.min(offset + page.items.length, page.total)} of ${page.total}`
                : "0 transactions"}
            </span>
            <button
              className="secondary-action"
              type="button"
              disabled={!canGoNext}
              onClick={() => setOffset(offset + pageSize)}
            >
              Next
            </button>
          </div>
        </section>

        {selectedId && (
          <section
            className="transaction-panel transaction-detail-panel"
            aria-labelledby="transaction-detail-title"
          >
            {selectedQuery.isLoading && (
              <p role="status">Loading transaction details...</p>
            )}
            {selectedQuery.data && (
              <>
                <div className="history-toolbar">
                  <div>
                    <p className="customer-card-label">Selected transaction</p>
                    <h2 id="transaction-detail-title">
                      {formatType(selectedQuery.data.transaction_type)}
                    </h2>
                  </div>
                  {selectedQuery.data.status === "PENDING" && (
                    <button
                      className="danger-action"
                      type="button"
                      disabled={cancelMutation.isPending}
                      onClick={() => void cancelSelected()}
                    >
                      {cancelMutation.isPending
                        ? "Cancelling..."
                        : "Cancel transaction"}
                    </button>
                  )}
                </div>
                <dl className="transaction-detail-grid">
                  <div>
                    <dt>Amount</dt>
                    <dd>£{selectedQuery.data.amount}</dd>
                  </div>
                  <div>
                    <dt>Status</dt>
                    <dd>{selectedQuery.data.status}</dd>
                  </div>
                  <div>
                    <dt>Reference</dt>
                    <dd>{selectedQuery.data.reference}</dd>
                  </div>
                  <div>
                    <dt>Description</dt>
                    <dd>
                      {selectedQuery.data.description || "No description"}
                    </dd>
                  </div>
                </dl>
                {message && (
                  <p className="transaction-message" role="status">
                    {message}
                  </p>
                )}
                <div className="history-logs">
                  <h3>Activity log</h3>
                  {logsQuery.isLoading && <p role="status">Loading log...</p>}
                  {logsQuery.data?.map((log) => (
                    <p key={log.id}>
                      <strong>{log.action}</strong> ·{" "}
                      {log.message || log.status} ·{" "}
                      {new Date(log.created_at).toLocaleString()}
                    </p>
                  ))}
                </div>
              </>
            )}
          </section>
        )}
      </section>
    </main>
  );
}
