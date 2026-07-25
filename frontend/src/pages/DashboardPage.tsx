import { useEffect, useState } from "react";
import { useNavigate } from "react-router";

import { logout } from "../api/authClient"; //
import {
  getCurrentUser,
  type UserResponse,
} from "../api/userClient";
import { clearTokens } from "../auth/tokenStorage";

export default function DashboardPage() {
  const navigate = useNavigate();
  const [user, setUser] = useState<UserResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoggingOut, setIsLoggingOut] = useState(false);

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
        reason: "Blocked"
      },
      {
        id: 2,
        name: "Noah",
        batch: "Andriod",
        client: "Barclays",
        reason: "Ending soon"
      }
    ]
  }



  
  useEffect(() => { //
    async function loadCurrentUser() {
      try {
        const currentUser = await getCurrentUser();
        setUser(currentUser);
      } catch {
        clearTokens();
        navigate("/login", { replace: true });
      } finally {
        setIsLoading(false);
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

  if (isLoading) {
    return (
      <main className="dashboard-state">
        <p>Loading your account...</p>
      </main>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <main className="dashboard-page">
      <section className="user-details-card">
        <header className="user-details-header">
          <p>Authenticated account</p>
          <h1>{user.username}</h1>
        </header>

        <dl className="user-details">
          <div>
            <dt>User ID</dt>
            <dd>{user.id}</dd>
          </div>

          <div>
            <dt>Username</dt>
            <dd>{user.username}</dd>
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