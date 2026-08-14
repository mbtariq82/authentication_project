import { useEffect, useState } from "react";
import type { AdminLoan, LoanStatus } from "../types/admin";
import { fetchLoans, updateLoanStatus } from "../api/adminApi";
import StatusBadge from "./StatusBadge";

const FILTERS: { key: LoanStatus | "all"; label: string }[] = [
  { key: "all", label: "All" },
  { key: "pending", label: "Pending" },
  { key: "approved", label: "Approved" },
  { key: "rejected", label: "Rejected" },
];

export default function LoansPanel() {
  const [loans, setLoans] = useState<AdminLoan[]>([]);
  const [filter, setFilter] = useState<LoanStatus | "all">("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actingOn, setActingOn] = useState<number | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchLoans();
      setLoans(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load loans");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function handleAction(loanId: number, status: LoanStatus) {
    setActingOn(loanId);
    try {
      const updated = await updateLoanStatus(loanId, status);
      setLoans((prev) => prev.map((l) => (l.id === loanId ? updated : l)));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Action failed");
    } finally {
      setActingOn(null);
    }
  }

  const visible = filter === "all" ? loans : loans.filter((l) => l.status === filter);

  return (
    <div className="panel">
      <div className="panel-header">
        <div className="panel-title">Loan applications</div>
        <div className="tabs">
          {FILTERS.map((f) => (
            <button
              key={f.key}
              className={`tab ${filter === f.key ? "active" : ""}`}
              onClick={() => setFilter(f.key)}
              type="button"
            >
              {f.label}
            </button>
          ))}
        </div>
      </div>

      {loading && <div className="panel-loading">Loading loans…</div>}
      {error && <div className="panel-error">{error}</div>}

      {!loading && !error && (
        <>
          {visible.length === 0 ? (
            <div className="panel-empty">No loans match this filter.</div>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>Customer</th>
                  <th>Loan type</th>
                  <th>Amount</th>
                  <th>Duration</th>
                  <th>Status</th>
                  <th style={{ textAlign: "right" }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {visible.map((loan) => (
                  <tr key={loan.id}>
                    <td>
                      <div className="customer">
                        <div className="customer-avatar">
                          {loan.customerName
                            .split(" ")
                            .map((n) => n[0])
                            .join("")
                            .slice(0, 2)}
                        </div>
                        <div>
                          <div className="customer-name">{loan.customerName}</div>
                          <div className="customer-email">{loan.customerEmail}</div>
                        </div>
                      </div>
                    </td>
                    <td style={{ textTransform: "capitalize" }}>{loan.loanType}</td>
                    <td className="mono-value">${loan.amount.toLocaleString()}</td>
                    <td>{loan.durationMonths} mo</td>
                    <td>
                      <StatusBadge status={loan.status} />
                    </td>
                    <td>
                      <div className="actions">
                        {loan.status === "pending" && (
                          <>
                            <button
                              className="btn approve"
                              disabled={actingOn === loan.id}
                              onClick={() => handleAction(loan.id, "approved")}
                            >
                              Approve
                            </button>
                            <button
                              className="btn reject"
                              disabled={actingOn === loan.id}
                              onClick={() => handleAction(loan.id, "rejected")}
                            >
                              Reject
                            </button>
                          </>
                        )}
                        {loan.status === "approved" && (
                          <button
                            className="btn reject"
                            disabled={actingOn === loan.id}
                            onClick={() => handleAction(loan.id, "cancelled")}
                          >
                            Cancel
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
          <div className="panel-footer">Showing {visible.length} of {loans.length} loans</div>
        </>
      )}
    </div>
  );
}
