import { useEffect, useState } from "react";
import { getCurrentUser, type UserResponse } from "../api/userClient";
import { useNavigate } from "react-router";
import { clearTokens } from "../auth/tokenStorage";
import { revokeRefreshToken } from "../api/authClient";

function DashboardPage() {
  const navigate = useNavigate();

  const [user, setUser] = useState<UserResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  async function handleLogout() {
    setIsLoggingOut(true);

    try {
      await revokeRefreshToken();
    } catch (error) {
      console.error("Backend logout failed", error);
    } finally {
      clearTokens();
      navigate("/login", { replace: true });
    }
  }

  useEffect(() => {
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
      <aside className="dashboard-sidebar">
        <div className="dashboard-brand">
          <div className="brand-icon">A</div>

          <div>
            <strong>AuthLab</strong>
            <p>Secure workspace</p>
          </div>
        </div>

        <nav className="dashboard-nav">
          <a className="dashboard-nav-link active" href="/dashboard">
            Overview
          </a>

          <a className="dashboard-nav-link" href="#">
            Profile
          </a>

          <a className="dashboard-nav-link" href="#">
            Security
          </a>

          <a className="dashboard-nav-link" href="#">
            Sessions
          </a>
        </nav>

        <div className="sidebar-user">
          <div className="user-avatar">
            {user.username.charAt(0).toUpperCase()}
          </div>

        </div>
      </aside>

      <section className="dashboard-content">
        <header className="dashboard-header">
          <div>
            <p className="dashboard-eyebrow">Account overview</p>
            <h1>Welcome back, {user.username}</h1>
            <p>Manage your account, security and active sessions.</p>
          </div>

          <button
            className="logout-button"
            type="button"
            onClick={handleLogout}
            disabled={isLoggingOut}
          >
            {isLoggingOut ? "Logging out..." : "Log out"}
          </button>
        </header>

        <section className="dashboard-summary-grid">
          <article className="dashboard-card profile-card">
            <div className="large-avatar">
              {user.username.charAt(0).toUpperCase()}
            </div>

            <div>
              <p className="card-label">Signed in as</p>
              <h2>{user.username}</h2>
            </div>
          </article>

          <article className="dashboard-card">
            <p className="card-label">User ID</p>
            <h2>#{user.id}</h2>

            <p className="card-description">
              Your unique identifier in the authentication system.
            </p>
          </article>
        </section>

        <section className="dashboard-panel">
          <div className="panel-heading">
            <div>
              <p className="card-label">Account information</p>
              <h2>Profile details</h2>
            </div>

            <button className="secondary-button" type="button">
              Edit profile
            </button>
          </div>

          <dl className="account-details">
            <div>
              <dt>Username</dt>
              <dd>{user.username}</dd>
            </div>

            <div>
              <dt>User ID</dt>
              <dd>{user.id}</dd>
            </div>
          </dl>
        </section>

        <section className="dashboard-panel">
          <div className="panel-heading">
            <div>
              <p className="card-label">Security</p>
              <h2>Authentication status</h2>
            </div>
          </div>

          <div className="security-item">
            <div>
              <strong>Password authentication</strong>
              <p>You signed in using your username and password.</p>
            </div>

            <span className="security-badge">Enabled</span>
          </div>

          <div className="security-item">
            <div>
              <strong>Access token</strong>
              <p>A valid access token is stored for this browser session.</p>
            </div>

            <span className="security-badge">Active</span>
          </div>
        </section>
      </section>
    </main>
  );
}

export default DashboardPage;
