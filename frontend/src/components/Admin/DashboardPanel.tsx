import { useEffect, useState } from "react";
import type { AdminUser } from "../../types/admin";
import { fetchUsers } from "../../api/adminApi";

export default function DashboardPanel() {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadDashboard() {
      try {
        setLoading(true);
        setError(null);

        const data = await fetchUsers();
        setUsers(data);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to load dashboard",
        );
      } finally {
        setLoading(false);
      }
    }

    loadDashboard();
  }, []);

  if (loading) {
    return <div className="panel-loading">Loading dashboard...</div>;
  }

  if (error) {
    return <div className="panel-error">{error}</div>;
  }

  const pendingUsers = users.filter((user) => user.user_status === "PENDING");

  const approvedUsers = users.filter((user) => user.user_status === "APPROVED");

  const rejectedUsers = users.filter((user) => user.user_status === "REJECTED");

  const totalUsers = users.length;

  const percentage = (count: number) => {
    if (totalUsers === 0) {
      return 0;
    }

    return Math.round((count / totalUsers) * 100);
  };

  return (
    <div className="dashboard-content">
      {/* Summary cards */}
      <div className="dashboard-stats">
        <div className="stat-card">
          <div className="stat-label">Total Users</div>
          <div className="stat-value">{totalUsers}</div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Pending Users</div>
          <div className="stat-value">{pendingUsers.length}</div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Approved Users</div>
          <div className="stat-value">{approvedUsers.length}</div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Rejected Users</div>
          <div className="stat-value">{rejectedUsers.length}</div>
        </div>
      </div>

      {/* Chart */}
      <div className="dashboard-chart-card">
        <h3>User Status Overview</h3>

        <div className="status-chart">
          <div className="chart-row">
            <span>Approved</span>

            <div className="chart-track">
              <div
                className="chart-bar approved-bar"
                style={{
                  width: `${percentage(approvedUsers.length)}%`,
                }}
              />
            </div>

            <strong>{approvedUsers.length}</strong>
          </div>

          <div className="chart-row">
            <span>Pending</span>

            <div className="chart-track">
              <div
                className="chart-bar pending-bar"
                style={{
                  width: `${percentage(pendingUsers.length)}%`,
                }}
              />
            </div>

            <strong>{pendingUsers.length}</strong>
          </div>

          <div className="chart-row">
            <span>Rejected</span>

            <div className="chart-track">
              <div
                className="chart-bar rejected-bar"
                style={{
                  width: `${percentage(rejectedUsers.length)}%`,
                }}
              />
            </div>

            <strong>{rejectedUsers.length}</strong>
          </div>
        </div>
      </div>

      {/* Pending users */}
      <div className="panel new-users-panel">
        <div className="panel-header">
          <div>
            <div className="panel-title">New Users</div>
            <div className="dashboard-description">
              Users waiting for approval
            </div>
          </div>

          <span className="pending-user-count">
            {pendingUsers.length} Pending
          </span>
        </div>

        {pendingUsers.length === 0 ? (
          <div className="panel-empty">No new users waiting for approval.</div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Customer</th>
                <th>Email</th>
                <th>Status</th>
              </tr>
            </thead>

            <tbody>
              {pendingUsers.map((user) => {
                const fullName = `${user.first_name} ${user.last_name}`.trim();

                const initials = `${user.first_name?.[0] ?? ""}${
                  user.last_name?.[0] ?? ""
                }`;

                return (
                  <tr key={user.id}>
                    <td>
                      <div className="customer">
                        <div className="customer-avatar">{initials}</div>

                        <div className="customer-name">{fullName}</div>
                      </div>
                    </td>

                    <td>{user.email}</td>

                    <td>
                      <span className="status pending">{user.user_status}</span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
