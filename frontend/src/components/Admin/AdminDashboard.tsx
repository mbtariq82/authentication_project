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
    subtitle: "Overview of customers and banking activity",
  },

  users: {
    title: "Customer review",
    subtitle: "Review and manage customer registrations",
  },

  accounts: {
    title: "Account review",
    subtitle: "Review and manage customer accounts",
  },

  loans: {
    title: "Loan review",
    subtitle: "Review and manage customer loan applications",
  },

  cards: {
    title: "Card review",
    subtitle: "Review and manage customer cards",
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
        {/* PAGE HEADER */}
        <div className="topbar">
          <div>
            <h1>{title}</h1>

            <p className="subtitle">{subtitle}</p>
          </div>
        </div>

        {/* DASHBOARD */}
        {activePanel === "dashboard" && <DashboardPanel />}

        {/* CUSTOMERS */}
        {activePanel === "users" && <UsersPanel />}

        {/* ACCOUNTS */}
        {activePanel === "accounts" && <AccountsPanel />}

        {/* LOANS */}
        {activePanel === "loans" && <LoansPanel />}

        {/* CARDS */}
        {activePanel === "cards" && <CardsPanel />}
      </main>
    </div>
  );
}
