import type { PanelKey } from "../types/admin";

interface SidebarProps {
  activePanel: PanelKey;
  onSelectPanel: (panel: PanelKey) => void;
  pendingCounts: Record<PanelKey, number>;
}

const NAV_ITEMS: { key: PanelKey; label: string; icon: JSX.Element }[] = [
  {
    key: "accounts",
    label: "Accounts",
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
        <rect x="2" y="6" width="20" height="14" rx="2" />
        <path d="M2 10h20" />
      </svg>
    ),
  },
  {
    key: "loans",
    label: "Loans",
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
        <rect x="2" y="5" width="20" height="14" rx="2" />
        <path d="M2 10h20M6 15h4" />
      </svg>
    ),
  },
  {
    key: "cards",
    label: "Cards",
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
        <rect x="2" y="5" width="20" height="14" rx="3" />
        <path d="M2 10h20" />
        <circle cx="16" cy="15" r="1.5" />
      </svg>
    ),
  },
];

export default function Sidebar({ activePanel, onSelectPanel, pendingCounts }: SidebarProps) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark">₿</div>
        <div>
          <div className="brand-text">Meridian Bank</div>
          <div className="brand-sub">Admin Console</div>
        </div>
      </div>

      <nav className="nav-list">
        <div className="nav-label">Review queue</div>
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
        <div className="avatar">RA</div>
        <div>
          <div className="admin-name">Riya Admin</div>
          <div className="admin-role">Compliance Officer</div>
        </div>
      </div>
    </aside>
  );
}
