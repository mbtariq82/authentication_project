import { useState } from "react";
import type { PanelKey } from "../types/admin";
import Sidebar from "./Sidebar";
import AccountsPanel from "./AccountsPanel";
import LoansPanel from "./LoansPanel";
import CardsPanel from "./CardsPanel";
import "../styles/admin-dashboard.css";

const PANEL_TITLES: Record<PanelKey, { title: string; subtitle: string }> = {
  accounts: { title: "Account review", subtitle: "Approve, reject, freeze, or close customer accounts" },
  loans: { title: "Loan review", subtitle: "Approve, reject, or cancel loan applications" },
  cards: { title: "Card review", subtitle: "Freeze or cancel issued debit and credit cards" },
};

export default function AdminDashboard() {
  const [activePanel, setActivePanel] = useState<PanelKey>("accounts");

  // Wire these up to real counts (e.g. from a small summary endpoint) once available.
  const pendingCounts: Record<PanelKey, number> = { accounts: 0, loans: 0, cards: 0 };

  const { title, subtitle } = PANEL_TITLES[activePanel];

  return (
    <div className="admin-app">
      <Sidebar activePanel={activePanel} onSelectPanel={setActivePanel} pendingCounts={pendingCounts} />

      <main className="main">
        <div className="topbar">
          <div>
            <h1>{title}</h1>
            <p className="subtitle">{subtitle}</p>
          </div>
          <div className="search">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="11" cy="11" r="8" />
              <path d="m21 21-4.3-4.3" />
            </svg>
            <input type="text" placeholder="Search by name or account no." />
          </div>
        </div>

        {activePanel === "accounts" && <AccountsPanel />}
        {activePanel === "loans" && <LoansPanel />}
        {activePanel === "cards" && <CardsPanel />}
      </main>
    </div>
  );
}
