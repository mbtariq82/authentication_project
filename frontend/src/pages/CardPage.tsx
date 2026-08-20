import { useEffect, useState } from "react";
import { Link } from "react-router";

import {
  getUserCard,
  getUnmaskedCard,
  createCard,
  toggleCardStatus,
  type CardDetailsResponse,
} from "../api/cardClient";

import CardVisual from "../components/Card/CardVisual";
import CardDetails from "../components/Card/CardDetails";
import CardActions from "../components/Card/CardActions";
import PasswordModal from "../components/Card/PasswordModal";
import OrderCardModal from "../components/Card/OrderCardModal";

import "../styles/card-page.css";

export default function CardPage() {
  const [card, setCard] = useState<CardDetailsResponse | null>(null);
  const [cardStatus, setCardStatus] = useState<"ACTIVE" | "FROZEN">("ACTIVE");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [password, setPassword] = useState("");
  const [showPasswordPrompt, setShowPasswordPrompt] = useState(false);
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [unmasking, setUnmasking] = useState(false);

  const [showOrderConfirmation, setShowOrderConfirmation] = useState(false);
  const [ordering, setOrdering] = useState(false);

  const [updatingStatus, setUpdatingStatus] = useState(false);

  const [cardDetailsVisible, setCardDetailsVisible] = useState(false);

  useEffect(() => {
    const loadCard = async () => {
      try {
        const card = await getUserCard();
        setCard(card);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load card.");
      } finally {
        setLoading(false);
      }
    };

    loadCard();
  }, []);

  const handleUnmaskCard = async () => {
    if (!password) {
      setPasswordError("Please enter your password.");
      return;
    }

    try {
      setUnmasking(true);
      setPasswordError(null);

      const unmaskedCard = await getUnmaskedCard(password);

      setCard(unmaskedCard);
      setCardDetailsVisible(true);
      setShowPasswordPrompt(false);
      setPassword("");
    } catch (err) {
      setPasswordError(
        err instanceof Error ? err.message : "Incorrect password.",
      );
    } finally {
      setUnmasking(false);
    }
  };

  const handleHideCardDetails = async () => {
    try {
      setError(null);

      const maskedCard = await getUserCard();

      setCard(maskedCard);
      setCardDetailsVisible(false);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to hide card details.",
      );
    }
  };

  const handleCreateCard = async () => {
    try {
      setOrdering(true);
      setError(null);

      await createCard();
      const formattedCard = await getUserCard();

      setCard(formattedCard);

      setCardStatus("ACTIVE");
      setShowOrderConfirmation(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create card.");
    } finally {
      setOrdering(false);
    }
  };

  const handleToggleCardStatus = async () => {
    try {
      setUpdatingStatus(true);
      setError(null);

      const response = await toggleCardStatus();

      if (response.status === "Frozen.") {
        setCardStatus("FROZEN");
      } else if (response.status === "Activated.") {
        setCardStatus("ACTIVE");
      }
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to update card status.",
      );
    } finally {
      setUpdatingStatus(false);
    }
  };

  if (loading) {
    return (
      <div className="card-page">
        <div className="card-page-container">
          <div className="card-loading">Loading card...</div>
        </div>
      </div>
    );
  }

  if (!card) {
    return (
      <div className="card-page">
        <div className="card-page-container">
          <div className="card-error">{error ?? "No card found."}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="card-page">
      <header className="customer-header">
        <div className="customer-brand-lockup">
          <span className="auth-brand-mark" aria-hidden="true">
            D
          </span>
          <span>Demo Bank</span>
        </div>

        <Link to="/account" className="customer-back">
          Back to account
        </Link>
      </header>

      <main className="card-page-container">
        <div className="card-content-layout">
          <section className="card-main">
            <header className="card-page-header">
              <p className="auth-eyebrow">Customer Card</p>
              <h1>My Card</h1>
              <p className="card-page-subtitle">
                Manage your card and view your card details.
              </p>
            </header>

            {error && <div className="card-error">{error}</div>}

            <CardVisual card={card} cardStatus={cardStatus} />
          </section>

          <section className="card-details-column">
            <CardActions
              cardStatus={cardStatus}
              updatingStatus={updatingStatus}
              cardDetailsVisible={cardDetailsVisible}
              onShowDetails={() => {
                setPassword("");
                setPasswordError(null);
                setShowPasswordPrompt(true);
              }}
              onHideDetails={handleHideCardDetails}
              onToggleStatus={handleToggleCardStatus}
              onOrderCard={() => setShowOrderConfirmation(true)}
            />
            <CardDetails card={card} cardStatus={cardStatus} />
          </section>
        </div>

        {showPasswordPrompt && (
          <PasswordModal
            password={password}
            passwordError={passwordError}
            unmasking={unmasking}
            onPasswordChange={setPassword}
            onConfirm={handleUnmaskCard}
            onClose={() => {
              setShowPasswordPrompt(false);
              setPassword("");
              setPasswordError(null);
            }}
          />
        )}

        {showOrderConfirmation && (
          <OrderCardModal
            ordering={ordering}
            onConfirm={handleCreateCard}
            onClose={() => setShowOrderConfirmation(false)}
          />
        )}
      </main>
    </div>
  );
}
