import { useEffect, useState } from "react";
import type { ReactNode } from "react";

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
  const [user, setUser] = useState<UserResponse | null>(null);

  useEffect(() => {
    async function loadUser() {
      try {
        const userData = await getUserProfile();
        setUser(userData);
      } catch (error) {
        console.error("Failed to load user profile:", error);
      }
    }

    loadUser();
  }, []);

  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark">MB</div>

        <div>
          <div className="brand-text">Meridian Bank</div>
          <div className="brand-sub">Admin Console</div>
        </div>
      </div>

      <nav className="nav-list">
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
          Dashboard
        </button>
        <div className="nav-label">Customer Management</div>

        {NAV_ITEMS.map((item) => (
          <button
            key={item.key}
            className={`nav-item ${activePanel === item.key ? "active" : ""}`}
            onClick={() => onSelectPanel(item.key)}
            type="button"
          >
            {item.icon}

            {item.label}

            {pendingCounts[item.key] > 0 && (
              <span className="nav-count">{pendingCounts[item.key]}</span>
            )}
          </button>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="avatar">
          {user
            ? `${user.first_name.charAt(0)}${user.last_name.charAt(0)}`
            : ""}
        </div>

        <div>
          <div className="admin-name">
            {user ? `${user.first_name} ${user.last_name}` : "Loading..."}
          </div>

          <div className="admin-role">{user?.role ?? ""}</div>
        </div>
      </div>
    </aside>
  );
}
