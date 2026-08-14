import { useEffect, useState } from "react";
import type { AdminCard, CardStatus } from "../types/admin";
import { fetchCards, updateCardStatus } from "../api/adminApi";
import StatusBadge from "./StatusBadge";

const FILTERS: { key: CardStatus | "all"; label: string }[] = [
  { key: "all", label: "All" },
  { key: "active", label: "Active" },
  { key: "frozen", label: "Frozen" },
  { key: "cancel", label: "Cancelled" },
];

export default function CardsPanel() {
  const [cards, setCards] = useState<AdminCard[]>([]);
  const [filter, setFilter] = useState<CardStatus | "all">("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actingOn, setActingOn] = useState<number | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchCards();
      setCards(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load cards");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function handleAction(cardId: number, status: CardStatus) {
    setActingOn(cardId);
    try {
      const updated = await updateCardStatus(cardId, status);
      setCards((prev) => prev.map((c) => (c.id === cardId ? updated : c)));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Action failed");
    } finally {
      setActingOn(null);
    }
  }

  const visible = filter === "all" ? cards : cards.filter((c) => c.status === filter);

  return (
    <div className="panel">
      <div className="panel-header">
        <div className="panel-title">Issued cards</div>
        <div className="tabs">
          {FILTERS.map((f) => (
            <button
              key={f.key}
              className={`tab ${filter === f.key ? "active" : ""}`}
              onClick={() => setFilter(f.key)}
              type="button"
            >
              {f.label}
            </button>
          ))}
        </div>
      </div>

      {loading && <div className="panel-loading">Loading cards…</div>}
      {error && <div className="panel-error">{error}</div>}

      {!loading && !error && (
        <>
          {visible.length === 0 ? (
            <div className="panel-empty">No cards match this filter.</div>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>Customer</th>
                  <th>Card number</th>
                  <th>Type</th>
                  <th>Status</th>
                  <th style={{ textAlign: "right" }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {visible.map((card) => (
                  <tr key={card.id}>
                    <td>
                      <div className="customer">
                        <div className="customer-avatar">
                          {card.customerName
                            .split(" ")
                            .map((n) => n[0])
                            .join("")
                            .slice(0, 2)}
                        </div>
                        <div>
                          <div className="customer-name">{card.customerName}</div>
                          <div className="customer-email">{card.customerEmail}</div>
                        </div>
                      </div>
                    </td>
                    <td className="mono-value">{card.cardNumberMasked}</td>
                    <td style={{ textTransform: "capitalize" }}>{card.cardType}</td>
                    <td>
                      <StatusBadge status={card.status} />
                    </td>
                    <td>
                      <div className="actions">
                        {card.status === "active" && (
                          <button
                            className="btn freeze"
                            disabled={actingOn === card.id}
                            onClick={() => handleAction(card.id, "frozen")}
                          >
                            Freeze
                          </button>
                        )}
                        {card.status === "frozen" && (
                          <button
                            className="btn approve"
                            disabled={actingOn === card.id}
                            onClick={() => handleAction(card.id, "active")}
                          >
                            Unfreeze
                          </button>
                        )}
                        {card.status !== "cancel" && (
                          <button
                            className="btn reject"
                            disabled={actingOn === card.id}
                            onClick={() => handleAction(card.id, "cancel")}
                          >
                            Cancel
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
          <div className="panel-footer">Showing {visible.length} of {cards.length} cards</div>
        </>
      )}
    </div>
  );
}
