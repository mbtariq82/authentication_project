import { useEffect, useState } from "react";
import { useNavigate } from "react-router";

import { logout } from "../api/authClient";
import {
  getAdminDashboard,
  type AdminDashboardResponse,
} from "../api/adminClient";
import { clearTokens } from "../auth/tokenStorage";

export default function DashboardPage() {
  const dashboardData = {
    summary: {
      total: 48,
      placed: 33,
      available: 8,
      endingSoon: 7,
    },
    consultantByBatch: [
      { batch: "Python", count: 20 },
      { batch: "Andriod", count: 16 },
      { batch: "Data", count: 12 },
    ],
    placementStatus: [
      { status: "Placed", count: 33 },
      { status: "Available", count: 8 },
      { status: "Ending soon", count: 7 },
    ],
    consultantsRequiringAttention: [
      {
        id: 1,
        name: "Bilal Tariq",
        batch: "Python",
        client: "Red Bull",
        reason: "Blocked",
      },
      {
        id: 2,
        name: "Noah",
        batch: "Andriod",
        client: "Barclays",
        reason: "Ending soon",
      },
    ],
  };
  const navigate = useNavigate();
  const [user, setUser] = useState<AdminDashboardResponse | null>(null);
  const [isLoggingOut, setIsLoggingOut] = useState(false); // for disabling logout button
  useEffect(() => {
    //
    async function loadCurrentUser() {
      try {
        const currentUser = await getAdminDashboard();
        setUser(currentUser);
      } catch {
        clearTokens();
        navigate("/admin/dashboard", { replace: true });
      }
    }
    void loadCurrentUser();
  }, [navigate]);

  async function handleLogout() {
    setIsLoggingOut(true);
    try {
      await logout();
    } catch (error) {
      console.error("Backend logout failed", error);
    } finally {
      clearTokens();
      navigate("/login", { replace: true });
    }
  }

  if (!user) {
    return null;
  }

  return (
    <main className="dashboard-page">
      <section className="dashboard-summary">
        <article className="summary-card">
          <h2>Total consultants</h2>
          <p>{dashboardData.summary.total}</p>
        </article>

        <article className="summary-card">
          <h2>Placed</h2>
          <p>{dashboardData.summary.placed}</p>
        </article>

        <article className="summary-card">
          <h2>Available</h2>
          <p>{dashboardData.summary.available}</p>
        </article>

        <article className="summary-card">
          <h2>Ending soon</h2>
          <p>{dashboardData.summary.endingSoon}</p>
        </article>
      </section>
      <section className="user-details-card">
        <header className="user-details-header">
          <p>Authenticated account</p>
        </header>

        <dl className="user-details">
          <div>
            <dt>User ID</dt>
            <dd>{user.id}</dd>
          </div>

          <div>
            <dt>Email</dt>
            <dd>{user.email}</dd>
          </div>

          <div>
            <dt>Role</dt>
            <dd>{user.role}</dd>
          </div>
        </dl>

        <button
          className="logout-button"
          type="button"
          onClick={handleLogout}
          disabled={isLoggingOut}
        >
          {isLoggingOut ? "Logging out..." : "Log out"}
        </button>
      </section>
    </main>
  );
}
