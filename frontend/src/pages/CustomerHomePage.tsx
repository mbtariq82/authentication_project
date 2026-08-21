import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router";

import { getUserProfile, type UserResponse } from "../api/userClient";
import { clearTokens } from "../auth/tokenStorage";
import { useAccount } from "../hooks/useAccount";
import { useAccountMutations } from "../hooks/useAccountMutations";
import CustomerNavigation from "../components/CustomerNavigation";
import FreezeAccountModal from "../components/Account/FreezeAccountModal";
import CloseAccountModal from "../components/Account/CloseAccountModal";

export default function CustomerHomePage() {
  const navigate = useNavigate();
  const [user, setUser] = useState<UserResponse | null>(null);

  const {
    data: account,
    isLoading: isAccountLoading,
    isError: isAccountError,
  } = useAccount();

  const { freeze, unfreeze, close } = useAccountMutations();

  const [showFreezeModal, setShowFreezeModal] = useState(false);
  const [showCloseModal, setShowCloseModal] = useState(false);
  const [closeReason, setCloseReason] = useState("");

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

  const balanceDisplay =
    account != null
      ? new Intl.NumberFormat("en-GB", {
          style: "currency",
          currency: "GBP",
        }).format(Number(account.balance))
      : null;
  const statusLabel = account?.account_status ?? "PENDING";
  const isApproved = statusLabel === "APPROVED";
  const isFrozen = statusLabel === "FROZEN";
  const balanceIsZero = account != null && Number(account.balance) === 0;

  return (
    <main className="customer-home">
      <CustomerNavigation user={user} />

      <section className="customer-content">
        <div className="customer-profile-intro">
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
                <h2>Account Unavailable</h2>
                <p>
                  Sorry, we couldn't find your account. Please try again later.
                </p>
              </div>
            ) : isAccountLoading || !account ? (
              <div>
                <p className="customer-card-label">Everyday account</p>
                <h2>Loading account…</h2>
              </div>
            ) : statusLabel === "PENDING" ? (
              <div>
                <p className="customer-card-label">Account Not Verified</p>
                <p>
                  Your account is pending and still in progress of being
                  verified. Please wait until the bank administrator has
                  verified your account.
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
                  {(isApproved || isFrozen) && (
                    <Link to="/card" className="customer-card-button">
                      View card
                    </Link>
                  )}

                  {isApproved && (
                    <button
                      type="button"
                      className="customer-card-button"
                      onClick={() => setShowFreezeModal(true)}
                    >
                      Freeze account
                    </button>
                  )}

                  {isFrozen && (
                    <button
                      type="button"
                      className="customer-card-button"
                      onClick={() => unfreeze.mutate()}
                      disabled={unfreeze.isPending}
                    >
                      {unfreeze.isPending ? "Unfreezing…" : "Unfreeze account"}
                    </button>
                  )}

                  {isApproved && (
                    <button
                      type="button"
                      className="customer-card-button danger"
                      onClick={() => setShowCloseModal(true)}
                      disabled={!balanceIsZero}
                      title={
                        balanceIsZero
                          ? undefined
                          : "You must empty your balance before closing."
                      }
                    >
                      Close account
                    </button>
                  )}
                </div>
              </>
            )}
            {showFreezeModal && (
              <FreezeAccountModal
                freezing={freeze.isPending}
                error={freeze.isError ? (freeze.error as Error).message : null}
                onConfirm={() =>
                  freeze.mutate(undefined, {
                    onSuccess: () => setShowFreezeModal(false),
                  })
                }
                onClose={() => {
                  freeze.reset();
                  setShowFreezeModal(false);
                }}
              />
            )}

            {showCloseModal && (
              <CloseAccountModal
                reason={closeReason}
                closing={close.isPending}
                error={close.isError ? (close.error as Error).message : null}
                onReasonChange={setCloseReason}
                onConfirm={() =>
                  close.mutate(closeReason.trim(), {
                    onSuccess: () => {
                      setShowCloseModal(false);
                      setCloseReason("");
                    },
                  })
                }
                onClose={() => {
                  close.reset();
                  setShowCloseModal(false);
                  setCloseReason("");
                }}
              />
            )}
          </article>
        </section>
      </section>
    </main>
  );
}
