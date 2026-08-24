import { useEffect, useState } from "react";
import type { PanelKey } from "../../types/admin";

import Sidebar from "./Sidebar";
import DashboardPanel from "./DashboardPanel";
import AccountsPanel from "./AccountsPanel";
import LoansPanel from "./LoansPanel";
import CardsPanel from "./CardsPanel";
import UsersPanel from "./UsersPanel";

import "../../styles/admin-dashboard.css";

import { searchAdmin, type AdminSearchResult } from "../../api/adminApi";

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
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<AdminSearchResult[]>([]);
  const [searching, setSearching] = useState(false);
  const [activePanel, setActivePanel] = useState<PanelKey>("dashboard");

  useEffect(() => {
    if (activePanel !== "users" && activePanel !== "accounts") {
      setSearchQuery("");
      setSearchResults([]);
      return;
    }

    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }

    const timer = setTimeout(async () => {
      try {
        setSearching(true);

        const data = await searchAdmin(searchQuery.trim());

        setSearchResults(data);
      } catch (error) {
        console.error("Search failed:", error);
        setSearchResults([]);
      } finally {
        setSearching(false);
      }
    }, 400);

    return () => clearTimeout(timer);
  }, [searchQuery, activePanel]);

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
          {activePanel === "users" && (
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

              <input
                type="text"
                value={searchQuery}
                placeholder="Search by name or account no."
                onChange={(event) => setSearchQuery(event.target.value)}
              />
            </div>
          )}
        </div>

        {/* DASHBOARD */}
        {activePanel === "dashboard" && <DashboardPanel />}

        {/* CUSTOMERS */}
        {(activePanel === "users" || activePanel === "accounts") && (
          <UsersPanel
            searchQuery={searchQuery}
            searchResults={searchResults}
            searching={searching}
          />
        )}

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
