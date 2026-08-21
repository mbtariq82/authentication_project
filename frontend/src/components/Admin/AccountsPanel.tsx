import { useEffect, useState } from "react";
import type { AdminAccount, AccountStatus } from "../../types/admin";

import { fetchAccounts, updateAccountStatus } from "../../api/adminApi";

import StatusBadge from "./StatusBadge";

const FILTERS: {
  key: AccountStatus | "all";
  label: string;
}[] = [
  { key: "all", label: "All" },
  { key: "PENDING", label: "Pending" },
  { key: "APPROVED", label: "Approved" },
  { key: "FROZEN", label: "Frozen" },
  { key: "CLOSED", label: "Closed" },
];

export default function AccountsPanel() {
  // ==========================
  // PAGINATION
  // ==========================

  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  const skip = (page - 1) * pageSize;

  // ==========================
  // ACCOUNTS
  // ==========================

  const [accounts, setAccounts] = useState<AdminAccount[]>([]);

  const [filter, setFilter] = useState<AccountStatus | "all">("all");

  const [loading, setLoading] = useState(true);

  const [error, setError] = useState<string | null>(null);

  const [actingOn, setActingOn] = useState<number | null>(null);

  // Detail modal
  const [selectedAccount, setSelectedAccount] = useState<AdminAccount | null>(
    null,
  );

  // Edit modal
  const [editingAccount, setEditingAccount] = useState<AdminAccount | null>(
    null,
  );

  // Selected action inside Edit modal
  const [pendingStatus, setPendingStatus] = useState<AccountStatus | null>(
    null,
  );

  // Reason for freeze / close
  const [actionReason, setActionReason] = useState("");

  // ==========================
  // LOAD ACCOUNTS
  // ==========================

  async function load() {
    setLoading(true);
    setError(null);

    try {
      const data = await fetchAccounts(skip, pageSize);

      setAccounts(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load accounts");
    } finally {
      setLoading(false);
    }
  }

  // Reload whenever page or page size changes
  useEffect(() => {
    void load();
  }, [page, pageSize]);

  // ==========================
  // UPDATE ACCOUNT STATUS
  // ==========================

  async function handleAction(
    accountId: number,
    status: AccountStatus,
    reason?: string,
  ) {
    setActingOn(accountId);
    setError(null);

    try {
      await updateAccountStatus(accountId, status, reason);

      // Fetch latest account data from backend
      await load();

      // Close edit modal
      setEditingAccount(null);

      setPendingStatus(null);
      setActionReason("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Action failed");
    } finally {
      setActingOn(null);
    }
  }

  // ==========================
  // EDIT MODAL
  // ==========================

  function openEditModal(account: AdminAccount) {
    setEditingAccount(account);

    setPendingStatus(null);
    setActionReason("");
    setError(null);
  }

  function closeEditModal() {
    setEditingAccount(null);

    setPendingStatus(null);
    setActionReason("");
    setError(null);
  }

  // ==========================
  // FILTER
  // ==========================

  const visible =
    filter === "all"
      ? accounts
      : accounts.filter((account) => account.account_status === filter);

  // ==========================
  // PAGINATION
  // ==========================

  function handlePageSizeChange(event: React.ChangeEvent<HTMLSelectElement>) {
    setPageSize(Number(event.target.value));

    // Go back to first page
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
        <div className="panel-title">Account applications</div>

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

      {loading && <div className="panel-loading">Loading accounts...</div>}

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
            <div className="panel-empty">No accounts match this filter.</div>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>Customer</th>
                  <th>Account no.</th>
                  <th>Type</th>
                  <th>Status</th>
                  <th>Opened</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>
                {visible.map((account) => {
                  const customerName = `${account.first_name ?? ""} ${
                    account.last_name ?? ""
                  }`.trim();

                  const initials = `${account.first_name?.[0] ?? ""}${
                    account.last_name?.[0] ?? ""
                  }`;

                  return (
                    <tr key={account.id}>
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
                              {account.email ?? "—"}
                            </div>
                          </div>
                        </div>
                      </td>

                      {/* ACCOUNT NUMBER */}

                      <td className="mono-value">
                        {account.account_number ?? "— pending —"}
                      </td>

                      {/* TYPE */}

                      <td
                        style={{
                          textTransform: "capitalize",
                        }}
                      >
                        {account.account_type}
                      </td>

                      {/* STATUS */}

                      <td>
                        <StatusBadge status={account.account_status} />
                      </td>

                      {/* CREATED */}

                      <td>
                        {account.created_at
                          ? new Date(account.created_at).toLocaleDateString()
                          : "—"}
                      </td>

                      {/* ACTIONS */}

                      <td>
                        <div className="actions">
                          <button
                            className="btn detail-btn"
                            type="button"
                            onClick={() => setSelectedAccount(account)}
                          >
                            👁 Detail
                          </button>

                          <button
                            className="btn edit-btn"
                            type="button"
                            onClick={() => openEditModal(account)}
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
                <option value={10}>10</option>

                <option value={20}>20</option>

                <option value={30}>30</option>
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
                disabled={accounts.length < pageSize}
                onClick={handleNext}
              >
                Next
              </button>
            </div>
          </div>
        </>
      )}

      {/* ==========================
          ACCOUNT DETAIL MODAL
      ========================== */}

      {selectedAccount && (
        <div className="modal-overlay">
          <div className="admin-modal">
            <div className="modal-header">
              <h2>Account Details</h2>

              <button
                type="button"
                className="modal-close"
                onClick={() => setSelectedAccount(null)}
              >
                ×
              </button>
            </div>

            <div className="user-details-grid">
              <div>
                <strong>Customer</strong>

                <p>
                  {selectedAccount.first_name} {selectedAccount.last_name}
                </p>
              </div>

              <div>
                <strong>Email</strong>

                <p>{selectedAccount.email ?? "—"}</p>
              </div>

              <div>
                <strong>User ID</strong>

                <p>{selectedAccount.user_id}</p>
              </div>

              <div>
                <strong>Account ID</strong>

                <p>{selectedAccount.id}</p>
              </div>

              <div>
                <strong>Account Number</strong>

                <p>{selectedAccount.account_number ?? "—"}</p>
              </div>

              <div>
                <strong>Sort Code</strong>

                <p>{selectedAccount.sort_code ?? "—"}</p>
              </div>

              <div>
                <strong>Account Type</strong>

                <p>{selectedAccount.account_type}</p>
              </div>

              <div>
                <strong>Branch</strong>

                <p>{selectedAccount.branch ?? "—"}</p>
              </div>

              <div>
                <strong>Balance</strong>

                <p>£{Number(selectedAccount.balance ?? 0).toLocaleString()}</p>
              </div>

              <div>
                <strong>Status</strong>

                <p>{selectedAccount.account_status}</p>
              </div>

              <div>
                <strong>Opened</strong>

                <p>
                  {selectedAccount.created_at
                    ? new Date(selectedAccount.created_at).toLocaleString()
                    : "—"}
                </p>
              </div>

              <div>
                <strong>Updated</strong>

                <p>
                  {selectedAccount.updated_at
                    ? new Date(selectedAccount.updated_at).toLocaleString()
                    : "—"}
                </p>
              </div>

              {selectedAccount.close_reason && (
                <div>
                  <strong>Status Reason</strong>

                  <p>{selectedAccount.close_reason}</p>
                </div>
              )}

              {selectedAccount.closed_at && (
                <div>
                  <strong>Closed At</strong>

                  <p>{new Date(selectedAccount.closed_at).toLocaleString()}</p>
                </div>
              )}
            </div>

            <div className="modal-actions">
              <button
                className="btn"
                type="button"
                onClick={() => setSelectedAccount(null)}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ==========================
          EDIT ACCOUNT MODAL
      ========================== */}

      {editingAccount && (
        <div className="modal-overlay">
          <div className="admin-modal">
            <div className="modal-header">
              <h2>Edit Account</h2>

              <button
                type="button"
                className="modal-close"
                onClick={closeEditModal}
              >
                ×
              </button>
            </div>

            {/* ACCOUNT INFO */}

            <div className="edit-user-info">
              <p>
                <strong>Customer:</strong> {editingAccount.first_name}{" "}
                {editingAccount.last_name}
              </p>

              <p>
                <strong>Account Number:</strong>{" "}
                {editingAccount.account_number ?? "—"}
              </p>

              <p>
                <strong>Current Status:</strong> {editingAccount.account_status}
              </p>
            </div>

            {/* ==========================
                PENDING
            ========================== */}

            {editingAccount.account_status === "PENDING" && (
              <div className="modal-actions">
                <button
                  className="btn approve"
                  type="button"
                  disabled={actingOn === editingAccount.id}
                  onClick={() => handleAction(editingAccount.id, "APPROVED")}
                >
                  {actingOn === editingAccount.id ? "Approving..." : "Approve"}
                </button>

                <button
                  className="btn reject"
                  type="button"
                  disabled={actingOn === editingAccount.id}
                  onClick={() => handleAction(editingAccount.id, "REJECTED")}
                >
                  {actingOn === editingAccount.id ? "Rejecting..." : "Reject"}
                </button>
              </div>
            )}

            {/* ==========================
                APPROVED
            ========================== */}

            {editingAccount.account_status === "APPROVED" && (
              <>
                {!pendingStatus && (
                  <div className="modal-actions">
                    <button
                      className="btn freeze"
                      type="button"
                      disabled={actingOn === editingAccount.id}
                      onClick={() => {
                        setPendingStatus("FROZEN");

                        setActionReason("");

                        setError(null);
                      }}
                    >
                      Freeze
                    </button>

                    <button
                      className="btn reject"
                      type="button"
                      disabled={actingOn === editingAccount.id}
                      onClick={() => {
                        setPendingStatus("CLOSED");

                        setActionReason("");

                        setError(null);
                      }}
                    >
                      Close
                    </button>
                  </div>
                )}

                {(pendingStatus === "FROZEN" || pendingStatus === "CLOSED") && (
                  <div className="reason-section">
                    <label className="reject-label">
                      <strong>
                        {pendingStatus === "FROZEN"
                          ? "Reason for freezing account"
                          : "Reason for closing account"}
                      </strong>
                    </label>

                    <textarea
                      className="reject-textarea"
                      value={actionReason}
                      onChange={(event) => setActionReason(event.target.value)}
                      placeholder={
                        pendingStatus === "FROZEN"
                          ? "Enter reason for freezing this account"
                          : "Enter reason for closing this account"
                      }
                      rows={4}
                    />

                    <div className="modal-actions">
                      <button
                        className="btn"
                        type="button"
                        onClick={() => {
                          setPendingStatus(null);

                          setActionReason("");

                          setError(null);
                        }}
                      >
                        Back
                      </button>

                      <button
                        className={
                          pendingStatus === "FROZEN"
                            ? "btn freeze"
                            : "btn reject"
                        }
                        type="button"
                        disabled={
                          !actionReason.trim() || actingOn === editingAccount.id
                        }
                        onClick={() =>
                          handleAction(
                            editingAccount.id,
                            pendingStatus,
                            actionReason.trim(),
                          )
                        }
                      >
                        {actingOn === editingAccount.id
                          ? "Updating..."
                          : pendingStatus === "FROZEN"
                            ? "Confirm Freeze"
                            : "Confirm Close"}
                      </button>
                    </div>
                  </div>
                )}
              </>
            )}

            {/* ==========================
                FROZEN
            ========================== */}

            {editingAccount.account_status === "FROZEN" && (
              <>
                {!pendingStatus && (
                  <div className="modal-actions">
                    <button
                      className="btn approve"
                      type="button"
                      disabled={actingOn === editingAccount.id}
                      onClick={() =>
                        handleAction(editingAccount.id, "APPROVED")
                      }
                    >
                      {actingOn === editingAccount.id
                        ? "Unfreezing..."
                        : "Unfreeze"}
                    </button>

                    <button
                      className="btn reject"
                      type="button"
                      disabled={actingOn === editingAccount.id}
                      onClick={() => {
                        setPendingStatus("CLOSED");

                        setActionReason("");

                        setError(null);
                      }}
                    >
                      Close
                    </button>
                  </div>
                )}

                {pendingStatus === "CLOSED" && (
                  <div className="reason-section">
                    <label className="reject-label">
                      <strong>Reason for closing account</strong>
                    </label>

                    <textarea
                      className="reject-textarea"
                      value={actionReason}
                      onChange={(event) => setActionReason(event.target.value)}
                      placeholder="Enter reason for closing this account"
                      rows={4}
                    />

                    <div className="modal-actions">
                      <button
                        className="btn"
                        type="button"
                        onClick={() => {
                          setPendingStatus(null);

                          setActionReason("");

                          setError(null);
                        }}
                      >
                        Back
                      </button>

                      <button
                        className="btn reject"
                        type="button"
                        disabled={
                          !actionReason.trim() || actingOn === editingAccount.id
                        }
                        onClick={() =>
                          handleAction(
                            editingAccount.id,
                            "CLOSED",
                            actionReason.trim(),
                          )
                        }
                      >
                        {actingOn === editingAccount.id
                          ? "Closing..."
                          : "Confirm Close"}
                      </button>
                    </div>
                  </div>
                )}
              </>
            )}

            {/* ==========================
                REJECTED
            ========================== */}

            {editingAccount.account_status === "REJECTED" && (
              <div className="modal-message">This account is rejected.</div>
            )}

            {/* ==========================
                CLOSED
            ========================== */}

            {editingAccount.account_status === "CLOSED" && (
              <div className="modal-message">
                <p>This account is closed.</p>

                {editingAccount.close_reason && (
                  <p>
                    <strong>Reason:</strong> {editingAccount.close_reason}
                  </p>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
