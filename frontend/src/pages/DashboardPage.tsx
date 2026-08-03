import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router";

import DashboardSummary from "../components/DashboardSummary";
import DashboardCharts from "../components/DashboardCharts";
import AttentionTable from "../components/AttentionTable";
import { logout } from "../api/authClient";
import { getAdminDashboard } from "../api/adminClient";
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
      { batch: "Python", count: 12 },
      { batch: "Java", count: 12 },
      { batch: "Andriod", count: 12 },
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
        name: "Tanushree Bante",
        batch: "Python",
        client: "Unassigned",
        reason: "Available",
      },
      {
        id: 3,
        name: "Fahadur Rahman",
        batch: "Python",
        client: "Unassigned",
        reason: "Available",
      },
      {
        id: 4,
        name: "Noah Amoo",
        batch: "Andriod",
        client: "Spotify",
        reason: "Placement delayed",
      },
      {
        id: 5,
        name: "Oluwapelumi Aregbesola",
        batch: "Andriod",
        client: "Uber",
        reason: "Client feedback required",
      },
    ],
  };
  const navigate = useNavigate();
  const [isLoggingOut, setIsLoggingOut] = useState(false); // for disabling logout button

  useEffect(() => {
    async function loadCurrentUser() {
      try {
        await getAdminDashboard();
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

  return (
    <main className="dashboard-page">
      <header className="header">
        <h1>ITC Dashboard</h1>
        <Link className="header-link" to="/admin/consultants">
          Consultants
        </Link>
        <button
          className="logout-button"
          onClick={handleLogout}
          disabled={isLoggingOut}
        >
          Logout
        </button>
      </header>
      <DashboardSummary
        total={dashboardData.summary.total}
        placed={dashboardData.summary.placed}
        available={dashboardData.summary.available}
        endingSoon={dashboardData.summary.endingSoon}
      />
      <DashboardCharts
        consultantsByBatch={dashboardData.consultantByBatch}
        placementStatus={dashboardData.placementStatus}
      />
      <AttentionTable
        consultants={dashboardData.consultantsRequiringAttention}
      />
    </main>
  );
}
