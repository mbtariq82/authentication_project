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
      <CustomerNavigation user={user} />

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
            <p className="auth-eyebrow">Customer Account</p>
            <h1>Welcome, {displayName}</h1>
          </div>
        </div>

        <section
          className="customer-grid customer-grid-single"
          aria-label="Account overview"
        >
          <article className="customer-primary-card">
            {isAccountError ? (
              <div>
                <p className="customer-card-label">Error</p>
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
            ) : statusLabel === "PENDING" ? (
              <div>
                <p className="customer-card-label">Everyday account</p>
                <p>
                  This account is not yet verified. Please allow a few days
                  while we get your account verified.
                </p>
              </div>
            ) : statusLabel === "CLOSED" ? (
              <div>
                <p className="customer-card-label">Account Closed</p>
                <p>
                  This account is closed. Please contact the bank administrator
                  if you need assistance.
                </p>
              </div>
            ) : (
              <>
                {statusLabel === "FROZEN" && (
                  <div className="customer-frozen-notice" role="alert">
                    This account is frozen. Transfers won't be accepted until
                    it's unfrozen.
                  </div>
                )}
                <div>
                  <p className="customer-card-label">
                    {account.account_number ??
                      "Account number pending assignment"}
                  </p>
                  <h2>{balanceDisplay}</h2>
                  <p>
                    {account.sort_code
                      ? `Sort code ${account.sort_code}`
                      : "Sort code pending assignment"}
                  </p>
                </div>
                <div className="customer-actions">
                  {(statusLabel === "APPROVED" || statusLabel === "FROZEN") && (
                    <Link to="/card" className="customer-card-button">
                      View card
                    </Link>
                  )}
                </div>
              </>
            )}
          </article>
        </section>
      </section>
    </main>
  );
}
