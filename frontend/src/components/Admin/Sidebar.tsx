import { useEffect, useRef, useState } from "react";
import type { ReactNode } from "react";
import { useNavigate } from "react-router";

import { logout } from "../../api/authClient";
import { clearTokens } from "../../auth/tokenStorage";
import { routes } from "../../routes";

import type { PanelKey } from "../../types/admin";

import { getUserProfile, type UserResponse } from "../../api/userClient";

interface SidebarProps {
  activePanel: PanelKey;
  onSelectPanel: (panel: PanelKey) => void;
  pendingCounts: Record<PanelKey, number>;
}

const NAV_ITEMS: {
  key: PanelKey;
  label: string;
  icon: ReactNode;
}[] = [
  {
    key: "users",
    label: "Users",
    icon: (
      <svg
        width="16"
        height="16"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.8"
      >
        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
        <circle cx="9" cy="7" r="4" />
        <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
        <path d="M16 3.13a4 4 0 0 1 0 7.75" />
      </svg>
    ),
  },

  {
    key: "accounts",
    label: "Accounts",
    icon: (
      <svg
        width="16"
        height="16"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.8"
      >
        <polygon points="12 2 21 8 3 8" />
        <line x1="6" y1="11" x2="6" y2="18" />
        <line x1="10" y1="11" x2="10" y2="18" />
        <line x1="14" y1="11" x2="14" y2="18" />
        <line x1="18" y1="11" x2="18" y2="18" />
        <line x1="3" y1="22" x2="21" y2="22" />
      </svg>
    ),
  },

  {
    key: "loans",
    label: "Loans",
    icon: (
      <svg
        width="16"
        height="16"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.8"
      >
        <rect x="2" y="6" width="20" height="12" rx="2" />

        <circle cx="12" cy="12" r="2" />

        <path d="M6 12h.01M18 12h.01" />
      </svg>
    ),
  },

  {
    key: "cards",
    label: "Cards",
    icon: (
      <svg
        width="16"
        height="16"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.8"
      >
        <rect x="2" y="5" width="20" height="14" rx="3" />

        <path d="M2 10h20" />

        <circle cx="16" cy="15" r="1.5" />
      </svg>
    ),
  },
];

export default function Sidebar({
  activePanel,
  onSelectPanel,
  pendingCounts,
}: SidebarProps) {
  const navigate = useNavigate();

  const [user, setUser] = useState<UserResponse | null>(null);

  const [showSettings, setShowSettings] = useState(false);

  const [isLoggingOut, setIsLoggingOut] = useState(false);

  const settingsRef = useRef<HTMLDivElement>(null);

  // ==============================
  // LOAD CURRENT ADMIN
  // ==============================

  useEffect(() => {
    async function loadUser() {
      try {
        const userData = await getUserProfile();

        setUser(userData);
      } catch (error) {
        console.error("Failed to load user profile:", error);
      }
    }

    void loadUser();
  }, []);

  // ==============================
  // CLOSE SETTINGS WHEN CLICKING
  // OUTSIDE
  // ==============================

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        settingsRef.current &&
        !settingsRef.current.contains(event.target as Node)
      ) {
        setShowSettings(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  // ==============================
  // LOGOUT
  // ==============================

  async function handleLogout() {
    try {
      setIsLoggingOut(true);

      await logout();
    } catch (error) {
      console.error("Logout failed:", error);
    } finally {
      clearTokens();

      navigate(routes.login, {
        replace: true,
      });
    }
  }

  // ==============================
  // PROFILE
  // ==============================

  function handleProfile() {
    setShowSettings(false);

    // Replace with routes.profile
    // if you already have that route.
    navigate("/profile");
  }

  return (
    <aside className="sidebar">
      {/* ==========================
          BRAND
      ========================== */}

      <div className="brand">
        <div className="brand-mark">MB</div>

        <div>
          <div className="brand-text">Meridian Bank</div>

          <div className="brand-sub">Admin Console</div>
        </div>
      </div>

      {/* ==========================
          NAVIGATION
      ========================== */}

      <nav className="nav-list" aria-label="Admin navigation">
        {/* DASHBOARD */}

        <button
          className={`nav-item ${activePanel === "dashboard" ? "active" : ""}`}
          onClick={() => onSelectPanel("dashboard")}
          type="button"
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.8"
          >
            <rect x="3" y="3" width="7" height="7" rx="1" />

            <rect x="14" y="3" width="7" height="7" rx="1" />

            <rect x="3" y="14" width="7" height="7" rx="1" />

            <rect x="14" y="14" width="7" height="7" rx="1" />
          </svg>

          <span>Dashboard</span>
        </button>

        {/* CUSTOMER MANAGEMENT */}

        <div className="nav-label">Customer Management</div>

        {NAV_ITEMS.map((item) => (
          <button
            key={item.key}
            className={`nav-item ${activePanel === item.key ? "active" : ""}`}
            onClick={() => onSelectPanel(item.key)}
            type="button"
          >
            {item.icon}

            <span>{item.label}</span>

            {pendingCounts[item.key] > 0 && (
              <span className="nav-count">{pendingCounts[item.key]}</span>
            )}
          </button>
        ))}
      </nav>

      {/* ==========================
          ADMIN FOOTER
      ========================== */}

      <div className="sidebar-footer">
        {/* AVATAR */}

        <div className="avatar">
          {user
            ? `${user.first_name?.charAt(0) ?? ""}${
                user.last_name?.charAt(0) ?? ""
              }`
            : ""}
        </div>

        {/* ADMIN INFORMATION */}

        <div className="admin-info">
          <div className="admin-name">
            {user ? `${user.first_name} ${user.last_name}` : "Loading..."}
          </div>

          <div className="admin-role">{user?.role ?? ""}</div>
        </div>

        {/* ======================
            SETTINGS
        ====================== */}

        <div className="admin-settings" ref={settingsRef}>
          <button
            type="button"
            className="settings-button"
            aria-label="Admin settings"
            aria-expanded={showSettings}
            onClick={() => setShowSettings((previous) => !previous)}
          >
            {/* GEAR ICON */}

            <svg
              width="22"
              height="22"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <circle cx="12" cy="12" r="3" />

              <path d="M19.4 15a1.7 1.7 0 0 0 .34 1.88l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06A1.7 1.7 0 0 0 15 19.4a1.7 1.7 0 0 0-1 .6 1.7 1.7 0 0 0-.4 1.1V21a2 2 0 1 1-4 0v-.09A1.7 1.7 0 0 0 8.6 19.4a1.7 1.7 0 0 0-1.88.34l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.7 1.7 0 0 0 4.6 15a1.7 1.7 0 0 0-.6-1 1.7 1.7 0 0 0-1.1-.4H3a2 2 0 1 1 0-4h.09A1.7 1.7 0 0 0 4.6 8.6a1.7 1.7 0 0 0-.34-1.88l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.7 1.7 0 0 0 9 4.6a1.7 1.7 0 0 0 1-.6 1.7 1.7 0 0 0 .4-1.1V3a2 2 0 1 1 4 0v.09A1.7 1.7 0 0 0 15.4 4.6a1.7 1.7 0 0 0 1.88-.34l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.7 1.7 0 0 0 19.4 9c.14.36.36.7.6 1 .28.3.67.47 1.1.4H21a2 2 0 1 1 0 4h-.09A1.7 1.7 0 0 0 19.4 15Z" />
            </svg>
          </button>

          {/* SETTINGS DROPDOWN */}

          {showSettings && (
            <div className="settings-menu">
              {/* PROFILE */}

              <button
                type="button"
                className="settings-menu-item"
                onClick={handleProfile}
              >
                <svg
                  width="17"
                  height="17"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <circle cx="12" cy="8" r="4" />

                  <path d="M4 21a8 8 0 0 1 16 0" />
                </svg>

                <span>Profile</span>
              </button>

              <div className="settings-menu-divider" />

              {/* LOGOUT */}

              <button
                type="button"
                className="settings-menu-item logout-item"
                onClick={() => void handleLogout()}
                disabled={isLoggingOut}
              >
                <svg
                  width="17"
                  height="17"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />

                  <polyline points="16 17 21 12 16 7" />

                  <line x1="21" y1="12" x2="9" y2="12" />
                </svg>

                <span>{isLoggingOut ? "Signing out..." : "Logout"}</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </aside>
  );
}
