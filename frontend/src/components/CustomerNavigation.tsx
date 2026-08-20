import { Link, useLocation, useNavigate } from "react-router";
import { useEffect, useRef, useState } from "react";

import { logout } from "../api/authClient";
import { getUserProfile, type UserResponse } from "../api/userClient";
import { clearTokens } from "../auth/tokenStorage";
import { routes } from "../routes";

type CustomerNavigationProps = {
  user?: UserResponse;
};

export default function CustomerNavigation({
  user: suppliedUser,
}: CustomerNavigationProps) {
  const location = useLocation();
  const navigate = useNavigate();
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const [loadedUser, setLoadedUser] = useState<UserResponse | null>(null);
  const [failedProfileImageUrl, setFailedProfileImageUrl] = useState<
    string | null
  >(null);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (suppliedUser) return;

    async function loadUser() {
      try {
        const currentUser = await getUserProfile();
        setLoadedUser(currentUser);
      } catch {
        clearTokens();
        navigate(routes.login, { replace: true });
      }
    }
    void loadUser();
  }, [navigate, suppliedUser]);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setIsDropdownOpen(false);
      }
    }
    if (isDropdownOpen) {
      document.addEventListener("mousedown", handleClickOutside);
      return () =>
        document.removeEventListener("mousedown", handleClickOutside);
    }
  }, [isDropdownOpen]);

  async function handleLogout() {
    try {
      setIsLoggingOut(true);
      await logout();
    } finally {
      clearTokens();
      navigate(routes.login, { replace: true });
    }
  }

  const user = suppliedUser ?? loadedUser;
  const showProfileImage =
    user?.profile_image_url && user.profile_image_url !== failedProfileImageUrl;
  const initials =
    user &&
    [user.first_name, user.last_name]
      .filter(Boolean)
      .map((name) => name[0])
      .join("")
      .toUpperCase()
      ? [user.first_name, user.last_name]
          .filter(Boolean)
          .map((name) => name[0])
          .join("")
          .toUpperCase()
      : user?.email[0].toUpperCase() || "U";

  return (
    <header className="customer-header">
      <Link className="customer-brand-lockup" to={routes.account}>
        <span className="auth-brand-mark" aria-hidden="true">
          N
        </span>
        <span>Nexa Bank</span>
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
        <div className="customer-profile-menu" ref={dropdownRef}>
          <button
            className="customer-profile-button"
            type="button"
            onClick={() => setIsDropdownOpen(!isDropdownOpen)}
            aria-label="Open profile menu"
            aria-expanded={isDropdownOpen}
          >
            {showProfileImage ? (
              <img
                className="customer-profile-avatar"
                src={user?.profile_image_url ?? undefined}
                alt="Profile"
                onError={() =>
                  setFailedProfileImageUrl(user?.profile_image_url ?? null)
                }
              />
            ) : (
              <span className="customer-profile-fallback" aria-hidden="true">
                {initials}
              </span>
            )}
          </button>
          {isDropdownOpen && (
            <div className="customer-profile-dropdown">
              <Link
                to={routes.profile}
                className="dropdown-item"
                onClick={() => setIsDropdownOpen(false)}
              >
                Profile
              </Link>
              <div className="dropdown-divider"></div>
              <button
                className="dropdown-item dropdown-logout"
                type="button"
                onClick={() => void handleLogout()}
                disabled={isLoggingOut}
              >
                {isLoggingOut ? "Signing out..." : "Log out"}
              </button>
            </div>
          )}
        </div>
      </nav>
    </header>
  );
}
