import { useEffect, useState } from "react";
import type { AdminAccount, AccountStatus } from "../../types/admin";
import { fetchAccounts, updateAccountStatus } from "../../api/adminApi";
import StatusBadge from "./StatusBadge";

const FILTERS: { key: AccountStatus | "all"; label: string }[] = [
  { key: "all", label: "All" },
  { key: "pending", label: "Pending" },
  { key: "approved", label: "Approved" },
  { key: "frozen", label: "Frozen" },
];

export default function AccountsPanel() {
  const [accounts, setAccounts] = useState<AdminAccount[]>([]);
  const [filter, setFilter] = useState<AccountStatus | "all">("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actingOn, setActingOn] = useState<number | null>(null);

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

    try {
      const updated = await updateAccountStatus(accountId, status);

      setAccounts((prev) =>
        prev.map((account) => (account.id === accountId ? updated : account)),
      );
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

      {loading && <div className="panel-loading">Loading accounts...</div>}

      {error && <div className="panel-error">{error}</div>}

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
                  <th style={{ textAlign: "right" }}>Actions</th>
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

                      <td className="mono-value">
                        {account.account_number ?? "— pending —"}
                      </td>

                      <td
                        style={{
                          textTransform: "capitalize",
                        }}
                      >
                        {account.account_type}
                      </td>

                      <td>
                        <StatusBadge status={account.account_status} />
                      </td>

                      <td>
                        {account.created_at
                          ? new Date(account.created_at).toLocaleDateString()
                          : "—"}
                      </td>

                      <td>
                        <div className="actions">
                          {account.account_status === "pending" && (
                            <>
                              <button
                                className="btn approve"
                                disabled={actingOn === account.id}
                                onClick={() =>
                                  handleAction(account.id, "approved")
                                }
                              >
                                Approve
                              </button>

                              <button
                                className="btn reject"
                                disabled={actingOn === account.id}
                                onClick={() =>
                                  handleAction(account.id, "rejected")
                                }
                              >
                                Reject
                              </button>
                            </>
                          )}

                          {account.account_status === "approved" && (
                            <>
                              <button
                                className="btn freeze"
                                disabled={actingOn === account.id}
                                onClick={() =>
                                  handleAction(account.id, "frozen")
                                }
                              >
                                Freeze
                              </button>

                              <button
                                className="btn reject"
                                disabled={actingOn === account.id}
                                onClick={() =>
                                  handleAction(account.id, "closed")
                                }
                              >
                                Close
                              </button>
                            </>
                          )}

                          {account.account_status === "frozen" && (
                            <>
                              <button
                                className="btn approve"
                                disabled={actingOn === account.id}
                                onClick={() =>
                                  handleAction(account.id, "approved")
                                }
                              >
                                Unfreeze
                              </button>

                              <button
                                className="btn reject"
                                disabled={actingOn === account.id}
                                onClick={() =>
                                  handleAction(account.id, "closed")
                                }
                              >
                                Close
                              </button>
                            </>
                          )}
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
    </div>
  );
}
