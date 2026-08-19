import { useEffect, useState } from "react";
import type { AdminUser, UserStatus } from "../../types/admin";
import { fetchUsers } from "../../api/adminApi";
import StatusBadge from "./StatusBadge";

const FILTERS: { key: UserStatus | "all"; label: string }[] = [
  { key: "all", label: "All" },
  { key: "PENDING", label: "Pending" },
  { key: "APPROVED", label: "Approved" },
  { key: "REJECTED", label: "Rejected" },
];

export default function UsersPanel() {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [filter, setFilter] = useState<UserStatus | "all">("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadUsers() {
    setLoading(true);
    setError(null);

    try {
      const data = await fetchUsers();
      setUsers(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load users");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadUsers();
  }, []);

  const visibleUsers =
    filter === "all"
      ? users
      : users.filter((user) => user.user_status === filter);

  return (
    <div className="panel">
      <div className="panel-header">
        <div className="panel-title">User applications</div>

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

      {loading && <div className="panel-loading">Loading users...</div>}

      {error && <div className="panel-error">{error}</div>}

      {!loading && !error && (
        <>
          {visibleUsers.length === 0 ? (
            <div className="panel-empty">No users match this filter.</div>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>Customer</th>
                  <th>Email</th>
                  <th>Role</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>

              <tbody>
                {visibleUsers.map((user) => {
                  const fullName = `${user.first_name ?? ""} ${
                    user.last_name ?? ""
                  }`.trim();

                  const initials = `${user.first_name?.[0] ?? ""}${
                    user.last_name?.[0] ?? ""
                  }`;

                  return (
                    <tr key={user.id}>
                      <td>
                        <div className="customer">
                          <div className="customer-avatar">
                            {initials || "NA"}
                          </div>

                          <div className="customer-name">
                            {fullName || "Unknown user"}
                          </div>
                        </div>
                      </td>

                      <td>{user.email}</td>

                      <td>{user.role}</td>

                      <td>
                        <StatusBadge status={user.user_status} />
                      </td>

                      <td></td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}

          <div className="panel-footer">
            Showing {visibleUsers.length} of {users.length} users
          </div>
        </>
      )}
    </div>
  );
}
