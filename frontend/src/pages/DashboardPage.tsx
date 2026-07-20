import { useEffect, useState } from "react";
import { useNavigate } from "react-router";

import { logout } from "../api/authClient"; //
import {
  getCurrentUser,
  type UserResponse,
} from "../api/userClient";
import { clearTokens } from "../auth/tokenStorage";

function DashboardPage() {
  const navigate = useNavigate();

  const [user, setUser] = useState<UserResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoggingOut, setIsLoggingOut] = useState(false);

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

export default DashboardPage;