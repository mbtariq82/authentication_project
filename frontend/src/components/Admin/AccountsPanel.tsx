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

  // Status selected from Edit modal
  const [pendingStatus, setPendingStatus] = useState<AccountStatus | null>(
    null,
  );

  // Reason for freeze / close
  const [actionReason, setActionReason] = useState("");

  async function load() {
    setLoading(true);
    setError(null);

    try {
      const data = await fetchAccounts();

      setAccounts(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load accounts");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function handleAction(
    accountId: number,
    status: AccountStatus,
    reason?: string,
  ) {
    setActingOn(accountId);
    setError(null);

    try {
      const updated = await updateAccountStatus(accountId, status, reason);

      setAccounts((prev) =>
        prev.map((account) =>
          account.id === accountId
            ? {
                ...account,
                ...updated,
              }
            : account,
        ),
      );

      setEditingAccount(null);
      setPendingStatus(null);
      setActionReason("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Action failed");
    } finally {
      setActingOn(null);
    }
  }

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

  const visible =
    filter === "all"
      ? accounts
      : accounts.filter((account) => account.account_status === filter);

  return (
    <div className="panel">
      {/* =========================
          HEADER
      ========================= */}

      <div className="panel-header">
        <div className="panel-title">Account applications</div>

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

      {/* =========================
          LOADING
      ========================= */}

      {loading && <div className="panel-loading">Loading accounts...</div>}

      {/* =========================
          ERROR
      ========================= */}

      {error && <div className="panel-error">{error}</div>}

      {/* =========================
          TABLE
      ========================= */}

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

                      {/* ACCOUNT TYPE */}

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

                      {/* CREATED DATE */}

                      <td>
                        {account.created_at
                          ? new Date(account.created_at).toLocaleDateString()
                          : "—"}
                      </td>

                      {/* ACTIONS */}

                      <td>
                        <div className="actions">
                          {/* DETAIL */}

                          <button
                            className="btn detail-btn"
                            type="button"
                            onClick={() => setSelectedAccount(account)}
                          >
                            👁 Detail
                          </button>

                          {/* EDIT */}

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

          <div className="panel-footer">
            Showing {visible.length} of {accounts.length} accounts
          </div>
        </>
      )}

      {/* ==================================
          ACCOUNT DETAIL MODAL
      ================================== */}

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
              {/* CUSTOMER */}

              <div>
                <strong>Customer</strong>

                <p>
                  {selectedAccount.first_name} {selectedAccount.last_name}
                </p>
              </div>

              {/* EMAIL */}

              <div>
                <strong>Email</strong>

                <p>{selectedAccount.email ?? "—"}</p>
              </div>

              {/* USER ID */}

              <div>
                <strong>User ID</strong>

                <p>{selectedAccount.user_id}</p>
              </div>

              {/* ACCOUNT ID */}

              <div>
                <strong>Account ID</strong>

                <p>{selectedAccount.id}</p>
              </div>

              {/* ACCOUNT NUMBER */}

              <div>
                <strong>Account Number</strong>

                <p>{selectedAccount.account_number ?? "—"}</p>
              </div>

              {/* SORT CODE */}

              <div>
                <strong>Sort Code</strong>

                <p>{selectedAccount.sort_code ?? "—"}</p>
              </div>

              {/* TYPE */}

              <div>
                <strong>Account Type</strong>

                <p>{selectedAccount.account_type}</p>
              </div>

              {/* BRANCH */}

              <div>
                <strong>Branch</strong>

                <p>{selectedAccount.branch ?? "—"}</p>
              </div>

              {/* BALANCE */}

              <div>
                <strong>Balance</strong>

                <p>{selectedAccount.balance ?? "0"}</p>
              </div>

              {/* STATUS */}

              <div>
                <strong>Status</strong>

                <p>{selectedAccount.account_status}</p>
              </div>

              {/* CREATED */}

              <div>
                <strong>Opened</strong>

                <p>
                  {selectedAccount.created_at
                    ? new Date(selectedAccount.created_at).toLocaleString()
                    : "—"}
                </p>
              </div>

              {/* UPDATED */}

              <div>
                <strong>Updated</strong>

                <p>
                  {selectedAccount.updated_at
                    ? new Date(selectedAccount.updated_at).toLocaleString()
                    : "—"}
                </p>
              </div>

              {/* CLOSE REASON */}

              {selectedAccount.close_reason && (
                <div>
                  <strong>Status Reason</strong>

                  <p>{selectedAccount.close_reason}</p>
                </div>
              )}

              {/* CLOSED AT */}

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

      {/* ==================================
          EDIT ACCOUNT MODAL
      ================================== */}

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

            {/* ACCOUNT INFORMATION */}

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

            {/* ==================================
                PENDING ACCOUNT
            ================================== */}

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
                  Reject
                </button>
              </div>
            )}

            {/* ==================================
                APPROVED ACCOUNT
            ================================== */}

            {editingAccount.account_status === "APPROVED" && (
              <>
                {/* INITIAL BUTTONS */}

                {!pendingStatus && (
                  <div className="modal-actions">
                    {/* FREEZE */}

                    <button
                      className="btn freeze"
                      type="button"
                      onClick={() => {
                        setPendingStatus("FROZEN");

                        setActionReason("");

                        setError(null);
                      }}
                    >
                      Freeze
                    </button>

                    {/* CLOSE */}

                    <button
                      className="btn reject"
                      type="button"
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

                {/* REASON FORM */}

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
                      {/* BACK */}

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

                      {/* CONFIRM */}

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

            {/* ==================================
                FROZEN ACCOUNT
            ================================== */}

            {editingAccount.account_status === "FROZEN" && (
              <>
                {/* INITIAL BUTTONS */}

                {!pendingStatus && (
                  <div className="modal-actions">
                    {/* UNFREEZE */}

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

                    {/* CLOSE */}

                    <button
                      className="btn reject"
                      type="button"
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

                {/* CLOSE REASON */}

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
                      {/* BACK */}

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

                      {/* CONFIRM CLOSE */}

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

            {/* ==================================
                REJECTED
            ================================== */}

            {editingAccount.account_status === "REJECTED" && (
              <div className="modal-message">This account is rejected.</div>
            )}

            {/* ==================================
                CLOSED
            ================================== */}

            {editingAccount.account_status === "CLOSED" && (
              <div className="modal-message">
                This account is closed.
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
