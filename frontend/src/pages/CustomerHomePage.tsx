import { useEffect, useState } from "react";
import { useNavigate } from "react-router";

import { logout } from "../api/authClient";
import { getUserProfile, type UserResponse } from "../api/userClient";
import { clearTokens } from "../auth/tokenStorage";

export default function CustomerHomePage() {
  const navigate = useNavigate();
  const [user, setUser] = useState<UserResponse | null>(null);
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  useEffect(() => {
    async function loadCurrentUser() {
      try {
        const currentUser = await getUserProfile();
        setUser(currentUser);
      } catch {
        clearTokens();
        navigate("/login", { replace: true });
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
    return (
      <main className="customer-home customer-home-loading">
        <p role="status">Loading your account…</p>
      </main>
    );
  }

  const displayName = user.first_name || "Customer";
  const fullName = [user.first_name, user.last_name].filter(Boolean).join(" ");

  return (
    <main className="customer-home">
      <header className="customer-header">
        <div className="customer-brand-lockup">
          <span className="auth-brand-mark" aria-hidden="true">
            D
          </span>
          <span>Demo Bank</span>
        </div>

        <button
          className="customer-logout"
          type="button"
          onClick={handleLogout}
          disabled={isLoggingOut}
        >
          {isLoggingOut ? "Signing out…" : "Sign out"}
        </button>
      </header>

      <section className="customer-content">
        <div className="customer-welcome">
          <p className="auth-eyebrow">Customer account</p>
          <h1>Welcome, {displayName}</h1>
          <p>Your secure Demo Bank sign-in is active.</p>
        </div>

        <aside className="customer-demo-notice">
          <strong>Demo environment</strong>
          <span>No real accounts, payments, or funds are used.</span>
        </aside>

        <section className="customer-grid" aria-label="Account overview">
          <article className="customer-primary-card">
            <div>
              <p className="customer-card-label">Everyday account</p>
              <h2>Account setup ready</h2>
              <p>
                Your banking products and balances will appear here as the
                demo account services are connected.
              </p>
            </div>
            <span className="customer-status">Secure access active</span>
          </article>

          <article className="customer-details-card">
            <header>
              <p className="customer-card-label">Your details</p>
              <h2>Customer profile</h2>
            </header>
            <dl>
              <div>
                <dt>Name</dt>
                <dd>{fullName || "Not provided"}</dd>
              </div>
              <div>
                <dt>Email</dt>
                <dd>{user.email}</dd>
              </div>
            </dl>
          </article>
        </section>
      </section>
    </main>
  );
}
