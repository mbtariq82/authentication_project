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

  async function handleAction(accountId: number, status: AccountStatus) {
    setActingOn(accountId);
    setError(null);

    try {
      const updated = await updateAccountStatus(accountId, status);

      setAccounts((prev) =>
        prev.map((account) => (account.id === accountId ? updated : account)),
      );

      setEditingAccount(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Action failed");
    } finally {
      setActingOn(null);
    }
  }

  const visible =
    filter === "all"
      ? accounts
      : accounts.filter((account) => account.account_status === filter);

  return (
    <div className="panel">
      {/* HEADER */}

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

      {/* LOADING */}

      {loading && <div className="panel-loading">Loading accounts...</div>}

      {/* ERROR */}

      {error && <div className="panel-error">{error}</div>}

      {/* TABLE */}

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

                      {/* OPENED */}

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
                            onClick={() => {
                              setEditingAccount(account);
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

          <div className="panel-footer">
            Showing {visible.length} of {accounts.length} accounts
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

                <p>{selectedAccount.balance ?? "0"}</p>
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
                  <strong>Close Reason</strong>

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
                onClick={() => setEditingAccount(null)}
              >
                ×
              </button>
            </div>

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

            {/* PENDING */}

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

            {/* APPROVED */}

            {editingAccount.account_status === "APPROVED" && (
              <div className="modal-actions">
                <button
                  className="btn freeze"
                  type="button"
                  disabled={actingOn === editingAccount.id}
                  onClick={() => handleAction(editingAccount.id, "FROZEN")}
                >
                  Freeze
                </button>

                <button
                  className="btn reject"
                  type="button"
                  disabled={actingOn === editingAccount.id}
                  onClick={() => handleAction(editingAccount.id, "CLOSED")}
                >
                  Close
                </button>
              </div>
            )}

            {/* FROZEN */}

            {editingAccount.account_status === "FROZEN" && (
              <div className="modal-actions">
                <button
                  className="btn approve"
                  type="button"
                  disabled={actingOn === editingAccount.id}
                  onClick={() => handleAction(editingAccount.id, "APPROVED")}
                >
                  Unfreeze
                </button>

                <button
                  className="btn reject"
                  type="button"
                  disabled={actingOn === editingAccount.id}
                  onClick={() => handleAction(editingAccount.id, "CLOSED")}
                >
                  Close
                </button>
              </div>
            )}

            {/* REJECTED */}

            {editingAccount.account_status === "REJECTED" && (
              <div className="modal-message">This account is rejected.</div>
            )}

            {/* CLOSED */}

            {editingAccount.account_status === "CLOSED" && (
              <div className="modal-message">This account is closed.</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
