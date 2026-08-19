import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router";

import { getUserProfile, type UserResponse } from "../api/userClient";
import { clearTokens } from "../auth/tokenStorage";
import { useAccount } from "../hooks/useAccount";
import CustomerNavigation from "../components/CustomerNavigation";

export default function CustomerHomePage() {
  const navigate = useNavigate();
  const [user, setUser] = useState<UserResponse | null>(null);
  const [profileImageFailed, setProfileImageFailed] = useState(false);

  const {
    data: account,
    isLoading: isAccountLoading,
    isError: isAccountError,
  } = useAccount();

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

  if (!user) {
    return (
      <main className="customer-home customer-home-loading">
        <p role="status">Loading your account…</p>
      </main>
    );
  }

  const displayName = user.first_name || "Customer";
  const fullName = [user.first_name, user.last_name].filter(Boolean).join(" ");
  const initials =
    [user.first_name, user.last_name]
      .filter(Boolean)
      .map((name) => name[0])
      .join("")
      .toUpperCase() || user.email[0].toUpperCase();
  const showProfileImage = user.profile_image_url && !profileImageFailed;

  const balanceDisplay =
    account != null
      ? new Intl.NumberFormat("en-GB", {
          style: "currency",
          currency: "GBP",
        }).format(Number(account.balance))
      : null;
  const statusLabel = account?.account_status ?? "Pending";

  return (
    <main className="customer-home">
      <CustomerNavigation />

      <section className="customer-content">
        <div className="customer-profile-intro">
          {showProfileImage ? (
            <img
              className="customer-profile-image"
              src={user.profile_image_url ?? undefined}
              alt={`${fullName || displayName}'s profile`}
              onError={() => setProfileImageFailed(true)}
            />
          ) : (
            <span className="customer-profile-fallback" aria-hidden="true">
              {initials}
            </span>
          )}

          <div className="customer-welcome">
            <p className="auth-eyebrow">Customer account</p>
            <h1>Welcome, {displayName}</h1>
            <p>Your secure Demo Bank sign-in is active.</p>
          </div>
        </div>

        <aside className="customer-demo-notice">
          <strong>Demo environment</strong>
          <span>No real accounts, payments, or funds are used.</span>
        </aside>

        <section className="customer-grid" aria-label="Account overview">
          <article className="customer-primary-card">
            {isAccountError ? (
              <div>
                <p className="customer-card-label">Everyday account</p>
                <h2>Account unavailable</h2>
                <p>
                  We couldn't load your account details right now. Please try
                  again shortly.
                </p>
              </div>
            ) : isAccountLoading || !account ? (
              <div>
                <p className="customer-card-label">Everyday account</p>
                <h2>Loading account…</h2>
              </div>
            ) : (
              <>
                <div>
                  <p className="customer-card-label">Everyday account</p>
                  <h2>{balanceDisplay}</h2>
                  <p>
                    {account.account_number
                      ? `Account number ${account.account_number}`
                      : "Account number pending assignment"}
                    {account.sort_code
                      ? ` · Sort code ${account.sort_code}`
                      : ""}
                  </p>
                </div>
                <div className="customer-actions">
                  <span className="customer-status">{statusLabel}</span>
                  <Link to="/card" className="customer-card-button">
                    View card
                  </Link>
                </div>
              </>
            )}
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
