import { Link, useLocation, useNavigate } from "react-router";
import { useState } from "react";

import { logout } from "../api/authClient";
import { clearTokens } from "../auth/tokenStorage";
import { routes } from "../routes";

export default function CustomerNavigation() {
  const location = useLocation();
  const navigate = useNavigate();
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  async function handleLogout() {
    try {
      setIsLoggingOut(true);
      await logout();
    } finally {
      clearTokens();
      navigate(routes.login, { replace: true });
    }
  }

  return (
    <header className="customer-header">
      <Link className="customer-brand-lockup" to={routes.account}>
        <span className="auth-brand-mark" aria-hidden="true">
          D
        </span>
        <span>Demo Bank</span>
      </Link>
      <nav className="customer-nav" aria-label="Customer navigation">
        <Link
          className={
            location.pathname === routes.account ? "customer-nav-active" : ""
          }
          to={routes.account}
        >
          Account
        </Link>
        <Link
          className={
            location.pathname === routes.beneficiaries
              ? "customer-nav-active"
              : ""
          }
          to={routes.beneficiaries}
        >
          Beneficiaries
        </Link>
        <Link
          className={
            location.pathname === routes.transactions
              ? "customer-nav-active"
              : ""
          }
          to={routes.transactions}
        >
          Move money
        </Link>
        <Link
          className={
            location.pathname === routes.transactionHistory
              ? "customer-nav-active"
              : ""
          }
          to={routes.transactionHistory}
        >
          History
        </Link>

        <Link
          className={
            location.pathname === routes.loans ? "customer-nav-active" : ""
          }
          to={routes.loans}
        >
          My Loans
        </Link>

        <button
          className="customer-logout"
          type="button"
          onClick={() => void handleLogout()}
          disabled={isLoggingOut}
        >
          {isLoggingOut ? "Signing out..." : "Sign out"}
        </button>
      </nav>
    </header>
  );
}
