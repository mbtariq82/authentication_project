import { useEffect, useState } from "react";
import type { AdminLoan, LoanStatus } from "../../types/admin";
import { fetchLoans, updateLoanStatus } from "../../api/adminApi";
import StatusBadge from "./StatusBadge";

const FILTERS: {
  key: LoanStatus | "all";
  label: string;
}[] = [
  { key: "all", label: "All" },
  { key: "PENDING", label: "Pending" },
  { key: "ACCEPTED", label: "Accepted" },
  { key: "REJECTED", label: "Rejected" },
];

export default function LoansPanel() {
  // Pagination
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);

  const skip = (page - 1) * pageSize;

  const [loans, setLoans] = useState<AdminLoan[]>([]);

  const [filter, setFilter] = useState<LoanStatus | "all">("all");

  const [loading, setLoading] = useState(true);

  const [error, setError] = useState<string | null>(null);

  const [actingOn, setActingOn] = useState<number | null>(null);

  // Detail modal
  const [selectedLoan, setSelectedLoan] = useState<AdminLoan | null>(null);

  // Edit modal
  const [editingLoan, setEditingLoan] = useState<AdminLoan | null>(null);

  async function load() {
    setLoading(true);
    setError(null);

    try {
      const data = await fetchLoans(skip, pageSize);

      setLoans(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load loans");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, [page, pageSize]);

  async function handleAction(loanId: number, status: LoanStatus) {
    setActingOn(loanId);
    setError(null);

    try {
      await updateLoanStatus(loanId, status);

      // Reload current page after update
      await load();

      setEditingLoan(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Action failed");
    } finally {
      setActingOn(null);
    }
  }

  const visible =
    filter === "all"
      ? loans
      : loans.filter((loan) => loan.current_loan_status === filter);

  function handlePageSizeChange(event: React.ChangeEvent<HTMLSelectElement>) {
    setPageSize(Number(event.target.value));

    // Always go back to first page
    setPage(1);
  }

  function handlePrevious() {
    setPage((previous) => Math.max(1, previous - 1));
  }

  function handleNext() {
    setPage((previous) => previous + 1);
  }

  return (
    <div className="panel">
      {/* ==========================
          HEADER
      ========================== */}

      <div className="panel-header">
        <div className="panel-title">Loan applications</div>

        <div className="tabs">
          {FILTERS.map((f) => (
            <button
              key={f.key}
              className={`tab ${filter === f.key ? "active" : ""}`}
              onClick={() => {
                setFilter(f.key);
              }}
              type="button"
            >
              {f.label}
            </button>
          ))}
        </div>
      </div>

      {/* ==========================
          LOADING
      ========================== */}

      {loading && <div className="panel-loading">Loading loans...</div>}

      {/* ==========================
          ERROR
      ========================== */}

      {error && <div className="panel-error">{error}</div>}

      {/* ==========================
          TABLE
      ========================== */}

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
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>
                {visible.map((loan) => {
                  const customerName = `${loan.first_name ?? ""} ${
                    loan.last_name ?? ""
                  }`.trim();

                  const initials = `${loan.first_name?.[0] ?? ""}${
                    loan.last_name?.[0] ?? ""
                  }`;

                  return (
                    <tr key={loan.id}>
                      {/* CUSTOMER */}

                      <td>
                        <div className="customer">
                          <div className="customer-avatar">
                            {initials || "NA"}
                          </div>

                          <div>
                            <div className="customer-name">
                              {customerName || "Unknown customer"}
                            </div>

                            <div className="customer-email">
                              {loan.email ?? "—"}
                            </div>
                          </div>
                        </div>
                      </td>

                      {/* LOAN TYPE */}

                      <td
                        style={{
                          textTransform: "capitalize",
                        }}
                      >
                        {loan.loan_type}
                      </td>

                      {/* AMOUNT */}

                      <td className="mono-value">
                        £{Number(loan.loan_amount).toLocaleString()}
                      </td>

                      {/* DURATION */}

                      <td>{loan.duration} months</td>

                      {/* STATUS */}

                      <td>
                        <StatusBadge status={loan.current_loan_status} />
                      </td>

                      {/* ACTIONS */}

                      <td>
                        <div className="actions">
                          <button
                            className="btn detail-btn"
                            type="button"
                            onClick={() => setSelectedLoan(loan)}
                          >
                            👁 Detail
                          </button>

                          <button
                            className="btn edit-btn"
                            type="button"
                            onClick={() => {
                              setEditingLoan(loan);

                              setError(null);
                            }}
                          >
                            ✎ Edit
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}

          {/* ==========================
              PAGINATION
          ========================== */}

          <div className="pagination">
            <div className="page-size">
              <span>Rows per page:</span>

              <select value={pageSize} onChange={handlePageSizeChange}>
                <option value={20}>20</option>

                <option value={40}>40</option>

                <option value={60}>60</option>
              </select>
            </div>

            <div className="page-controls">
              <button
                className="pagination-btn"
                type="button"
                disabled={page === 1}
                onClick={handlePrevious}
              >
                Previous
              </button>

              <span className="page-number">Page {page}</span>

              <button
                className="pagination-btn"
                type="button"
                disabled={loans.length < pageSize}
                onClick={handleNext}
              >
                Next
              </button>
            </div>
          </div>
        </>
      )}

      {/* ==========================
          LOAN DETAIL MODAL
      ========================== */}

      {selectedLoan && (
        <div className="modal-overlay">
          <div className="admin-modal">
            <div className="modal-header">
              <h2>Loan Details</h2>

              <button
                type="button"
                className="modal-close"
                onClick={() => setSelectedLoan(null)}
              >
                ×
              </button>
            </div>

            <div className="user-details-grid">
              <div>
                <strong>Customer</strong>

                <p>
                  {selectedLoan.first_name} {selectedLoan.last_name}
                </p>
              </div>

              <div>
                <strong>Email</strong>

                <p>{selectedLoan.email ?? "—"}</p>
              </div>

              <div>
                <strong>Loan ID</strong>

                <p>{selectedLoan.id}</p>
              </div>

              <div>
                <strong>Loan Type</strong>

                <p>{selectedLoan.loan_type}</p>
              </div>

              <div>
                <strong>Loan Amount</strong>

                <p>£{Number(selectedLoan.loan_amount).toLocaleString()}</p>
              </div>

              <div>
                <strong>Duration</strong>

                <p>{selectedLoan.duration} months</p>
              </div>

              <div>
                <strong>Interest</strong>

                <p>{selectedLoan.interest}%</p>
              </div>

              <div>
                <strong>EMI</strong>

                <p>£{Number(selectedLoan.emi).toLocaleString()}</p>
              </div>

              <div>
                <strong>Status</strong>

                <p>{selectedLoan.current_loan_status}</p>
              </div>

              {selectedLoan.user_id !== undefined && (
                <div>
                  <strong>User ID</strong>

                  <p>{selectedLoan.user_id}</p>
                </div>
              )}
            </div>

            <div className="modal-actions">
              <button
                className="btn"
                type="button"
                onClick={() => setSelectedLoan(null)}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ==========================
          EDIT LOAN MODAL
      ========================== */}

      {editingLoan && (
        <div className="modal-overlay">
          <div className="admin-modal">
            <div className="modal-header">
              <h2>Edit Loan</h2>

              <button
                type="button"
                className="modal-close"
                onClick={() => setEditingLoan(null)}
              >
                ×
              </button>
            </div>

            <div className="edit-user-info">
              <p>
                <strong>Customer:</strong> {editingLoan.first_name}{" "}
                {editingLoan.last_name}
              </p>

              <p>
                <strong>Loan Type:</strong> {editingLoan.loan_type}
              </p>

              <p>
                <strong>Amount:</strong> £
                {Number(editingLoan.loan_amount).toLocaleString()}
              </p>

              <p>
                <strong>Duration:</strong> {editingLoan.duration} months
              </p>

              <p>
                <strong>Current Status:</strong>{" "}
                {editingLoan.current_loan_status}
              </p>
            </div>

            {/* PENDING */}

            {editingLoan.current_loan_status === "PENDING" && (
              <div className="modal-actions">
                <button
                  className="btn approve"
                  type="button"
                  disabled={actingOn === editingLoan.id}
                  onClick={() => handleAction(editingLoan.id, "ACCEPTED")}
                >
                  {actingOn === editingLoan.id ? "Accepting..." : "Accept"}
                </button>

                <button
                  className="btn reject"
                  type="button"
                  disabled={actingOn === editingLoan.id}
                  onClick={() => handleAction(editingLoan.id, "REJECTED")}
                >
                  {actingOn === editingLoan.id ? "Rejecting..." : "Reject"}
                </button>
              </div>
            )}

            {/* ACCEPTED */}

            {editingLoan.current_loan_status === "ACCEPTED" && (
              <div className="modal-message">This loan has been accepted.</div>
            )}

            {/* REJECTED */}

            {editingLoan.current_loan_status === "REJECTED" && (
              <div className="modal-message">This loan has been rejected.</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
