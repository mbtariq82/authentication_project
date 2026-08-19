import { useState } from "react";
import type { PanelKey } from "../../types/admin";

import Sidebar from "./Sidebar";
import DashboardPanel from "./DashboardPanel";
import AccountsPanel from "./AccountsPanel";
import LoansPanel from "./LoansPanel";
import CardsPanel from "./CardsPanel";
import UsersPanel from "./UsersPanel";

import "../../styles/admin-dashboard.css";

const PANEL_TITLES: Record<PanelKey, { title: string; subtitle: string }> = {
  dashboard: {
    title: "Dashboard",
    subtitle: "Overview of users and banking activity",
  },
  users: {
    title: "User review",
    subtitle: "Approve or reject new customer registrations",
  },

  accounts: {
    title: "Account review",
    subtitle: "Approved, rejected, pending, or closed customer accounts",
  },

  loans: {
    title: "Loan review",
    subtitle: "Approve, reject, or cancel loan applications",
  },

  cards: {
    title: "Card review",
    subtitle: "Freeze or cancel issued debit and credit cards",
  },
};

export default function AdminDashboard() {
  const [activePanel, setActivePanel] = useState<PanelKey>("dashboard");

  const pendingCounts: Record<PanelKey, number> = {
    dashboard: 0,
    users: 0,
    accounts: 0,
    loans: 0,
    cards: 0,
  };

  const { title, subtitle } = PANEL_TITLES[activePanel];

  return (
    <div className="admin-app">
      <Sidebar
        activePanel={activePanel}
        onSelectPanel={setActivePanel}
        pendingCounts={pendingCounts}
      />

      <main className="main">
        <div className="topbar">
          <div>
            <h1>{title}</h1>
            <p className="subtitle">{subtitle}</p>
          </div>

          {activePanel !== "dashboard" && (
            <div className="search">
              <svg
                width="15"
                height="15"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <circle cx="11" cy="11" r="8" />
                <path d="m21 21-4.3-4.3" />
              </svg>

              <input type="text" placeholder="Search by name or account no." />
            </div>
          )}
        </div>

        {activePanel === "dashboard" && <DashboardPanel />}
        {activePanel === "users" && <UsersPanel />}

        {activePanel === "accounts" && <AccountsPanel />}
        {activePanel === "loans" && <LoansPanel />}
        {activePanel === "cards" && <CardsPanel />}
      </main>
    </div>
  );
}
