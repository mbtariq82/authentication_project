import { MessageCircle, Minus, X } from "lucide-react";
import { useEffect, useState } from "react";
import "./ChatWidget.css";

const CHAT_WIDGET_OPEN_KEY = "chat_widget_open";

function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    setIsOpen(sessionStorage.getItem(CHAT_WIDGET_OPEN_KEY) === "true");
  }, []);

  function updateOpenState(nextIsOpen: boolean) {
    setIsOpen(nextIsOpen);
    sessionStorage.setItem(CHAT_WIDGET_OPEN_KEY, String(nextIsOpen));
  }

  if (!isOpen) {
    return (
      <button
        className="chat-widget-launcher"
        type="button"
        onClick={() => updateOpenState(true)}
        aria-label="Open banking assistant"
        title="Open banking assistant"
      >
        <MessageCircle aria-hidden="true" size={24} />
      </button>
    );
  }

  return (
    <aside className="chat-widget-panel" aria-label="Banking assistant">
      <header className="chat-widget-header">
        <div className="chat-widget-heading">
          <span className="chat-widget-brand-mark" aria-hidden="true">
            N
          </span>
          <div>
            <p>Nexa assistant</p>
            <span>Available to help</span>
          </div>
        </div>
        <div className="chat-widget-actions">
          <button
            type="button"
            onClick={() => updateOpenState(false)}
            aria-label="Minimize banking assistant"
            title="Minimize"
          >
            <Minus aria-hidden="true" size={18} />
          </button>
          <button
            type="button"
            onClick={() => updateOpenState(false)}
            aria-label="Close banking assistant"
            title="Close"
          >
            <X aria-hidden="true" size={18} />
          </button>
        </div>
      </header>
      <div className="chat-widget-placeholder">
        <MessageCircle aria-hidden="true" size={28} />
        <p>How can we help today?</p>
      </div>
    </aside>
  );
}

export default ChatWidget;
