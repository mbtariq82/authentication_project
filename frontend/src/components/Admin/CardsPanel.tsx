import { useEffect, useState } from "react";
import type { AdminCard, CardStatus } from "../../types/admin";
import { fetchCards, updateCardStatus } from "../../api/adminApi";
import StatusBadge from "./StatusBadge";

const FILTERS: {
  key: CardStatus | "all";
  label: string;
}[] = [
  { key: "all", label: "All" },
  { key: "ACTIVE", label: "Active" },
  { key: "FROZEN", label: "Frozen" },
  { key: "CLOSED", label: "Closed" },
];

export default function CardsPanel() {
  const [cards, setCards] = useState<AdminCard[]>([]);

  const [filter, setFilter] = useState<CardStatus | "all">("all");

  const [loading, setLoading] = useState(true);

  const [error, setError] = useState<string | null>(null);

  const [actingOn, setActingOn] = useState<number | null>(null);

  // Detail modal
  const [selectedCard, setSelectedCard] = useState<AdminCard | null>(null);

  // Edit modal
  const [editingCard, setEditingCard] = useState<AdminCard | null>(null);

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
    setError(null);

    try {
      const updated = await updateCardStatus(cardId, status);

      setCards((prev) =>
        prev.map((card) =>
          card.id === cardId
            ? {
                ...card,
                ...updated,
              }
            : card,
        ),
      );

      setEditingCard(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Action failed");
    } finally {
      setActingOn(null);
    }
  }

  const visible =
    filter === "all" ? cards : cards.filter((card) => card.status === filter);

  return (
    <div className="panel">
      {/* HEADER */}

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

      {/* LOADING */}

      {loading && <div className="panel-loading">Loading cards...</div>}

      {/* ERROR */}

      {error && <div className="panel-error">{error}</div>}

      {/* TABLE */}

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
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>
                {visible.map((card) => {
                  const customerName = `${card.first_name ?? ""} ${
                    card.last_name ?? ""
                  }`.trim();

                  const initials = `${card.first_name?.[0] ?? ""}${
                    card.last_name?.[0] ?? ""
                  }`;

                  return (
                    <tr key={card.id}>
                      {/* CUSTOMER */}

                      <td>
                        <div className="customer">
                          <div className="customer-avatar">
                            {initials || "NA"}
                          </div>

                          <div>
                            <div className="customer-name">
                              {customerName || "Unknown customer"}
                            </div>

                            <div className="customer-email">
                              {card.email ?? "—"}
                            </div>
                          </div>
                        </div>
                      </td>

                      {/* CARD NUMBER */}

                      <td className="mono-value">{card.card_number ?? "—"}</td>

                      {/* STATUS */}

                      <td>
                        <StatusBadge status={card.status} />
                      </td>

                      {/* ACTIONS */}

                      <td>
                        <div className="actions">
                          <button
                            className="btn detail-btn"
                            type="button"
                            onClick={() => setSelectedCard(card)}
                          >
                            👁 Detail
                          </button>

                          <button
                            className="btn edit-btn"
                            type="button"
                            onClick={() => {
                              setEditingCard(card);
                              setError(null);
                            }}
                          >
                            ✎ Edit
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}

          <div className="panel-footer">
            Showing {visible.length} of {cards.length} cards
          </div>
        </>
      )}

      {/* ==========================
          CARD DETAIL MODAL
      ========================== */}

      {selectedCard && (
        <div className="modal-overlay">
          <div className="admin-modal">
            <div className="modal-header">
              <h2>Card Details</h2>

              <button
                type="button"
                className="modal-close"
                onClick={() => setSelectedCard(null)}
              >
                ×
              </button>
            </div>

            <div className="user-details-grid">
              <div>
                <strong>Customer</strong>
                <p>
                  {selectedCard.first_name} {selectedCard.last_name}
                </p>
              </div>

              <div>
                <strong>Email</strong>
                <p>{selectedCard.email ?? "—"}</p>
              </div>

              <div>
                <strong>Card ID</strong>
                <p>{selectedCard.id}</p>
              </div>

              <div>
                <strong>Account ID</strong>
                <p>{selectedCard.account_id}</p>
              </div>

              <div>
                <strong>Card Number</strong>
                <p>{selectedCard.card_number ?? "—"}</p>
              </div>

              <div>
                <strong>Status</strong>
                <p>{selectedCard.status}</p>
              </div>

              <div>
                <strong>Expiry Date</strong>
                <p>
                  {selectedCard.expiry_date
                    ? new Date(selectedCard.expiry_date).toLocaleDateString()
                    : "—"}
                </p>
              </div>

              <div>
                <strong>Created At</strong>
                <p>
                  {selectedCard.created_at
                    ? new Date(selectedCard.created_at).toLocaleString()
                    : "—"}
                </p>
              </div>

              {selectedCard.user_id !== undefined && (
                <div>
                  <strong>User ID</strong>
                  <p>{selectedCard.user_id}</p>
                </div>
              )}
            </div>

            <div className="modal-actions">
              <button
                className="btn"
                type="button"
                onClick={() => setSelectedCard(null)}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ==========================
          EDIT CARD MODAL
      ========================== */}

      {editingCard && (
        <div className="modal-overlay">
          <div className="admin-modal">
            <div className="modal-header">
              <h2>Edit Card</h2>

              <button
                type="button"
                className="modal-close"
                onClick={() => setEditingCard(null)}
              >
                ×
              </button>
            </div>

            <div className="edit-user-info">
              <p>
                <strong>Customer:</strong> {editingCard.first_name}{" "}
                {editingCard.last_name}
              </p>

              <p>
                <strong>Card Number:</strong> {editingCard.card_number ?? "—"}
              </p>

              <p>
                <strong>Current Status:</strong> {editingCard.status}
              </p>
            </div>

            {/* ACTIVE */}

            {editingCard.status === "ACTIVE" && (
              <div className="modal-actions">
                <button
                  className="btn freeze"
                  type="button"
                  disabled={actingOn === editingCard.id}
                  onClick={() => handleAction(editingCard.id, "FROZEN")}
                >
                  {actingOn === editingCard.id ? "Freezing..." : "Freeze"}
                </button>

                <button
                  className="btn reject"
                  type="button"
                  disabled={actingOn === editingCard.id}
                  onClick={() => handleAction(editingCard.id, "CLOSED")}
                >
                  Close
                </button>
              </div>
            )}

            {/* FROZEN */}

            {editingCard.status === "FROZEN" && (
              <div className="modal-actions">
                <button
                  className="btn approve"
                  type="button"
                  disabled={actingOn === editingCard.id}
                  onClick={() => handleAction(editingCard.id, "ACTIVE")}
                >
                  {actingOn === editingCard.id ? "Unfreezing..." : "Unfreeze"}
                </button>

                <button
                  className="btn reject"
                  type="button"
                  disabled={actingOn === editingCard.id}
                  onClick={() => handleAction(editingCard.id, "CLOSED")}
                >
                  Close
                </button>
              </div>
            )}
            {/* CLOSED */}

            {editingCard.status === "CLOSED" && (
              <div className="modal-message">This card is closed.</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
