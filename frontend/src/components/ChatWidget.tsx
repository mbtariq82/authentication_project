import {
  LoaderCircle,
  MessageCircle,
  Minus,
  RefreshCw,
  Send,
  X,
} from "lucide-react";
import { useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import { resetGuestChatSession, sendChatMessage } from "../api/chatbotClient";
import "./ChatWidget.css";

const CHAT_WIDGET_OPEN_KEY = "chat_widget_open";

type ChatMessage = {
  id: string;
  content: string;
  sender: "assistant" | "user";
};

const welcomeMessage: ChatMessage = {
  id: "welcome",
  content: "Hi, I am Nexa. How can I help today?",
  sender: "assistant",
};

function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [draft, setDraft] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([welcomeMessage]);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [lastSubmittedMessage, setLastSubmittedMessage] = useState<
    string | null
  >(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setIsOpen(sessionStorage.getItem(CHAT_WIDGET_OPEN_KEY) === "true");
  }, []);

  function updateOpenState(nextIsOpen: boolean) {
    setIsOpen(nextIsOpen);
    sessionStorage.setItem(CHAT_WIDGET_OPEN_KEY, String(nextIsOpen));
  }

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [errorMessage, isLoading, messages]);

  function clearChat() {
    setDraft("");
    setMessages([welcomeMessage]);
    setErrorMessage(null);
    setLastSubmittedMessage(null);
    resetGuestChatSession();
  }

  async function attemptMessage(message: string) {
    setIsLoading(true);
    setErrorMessage(null);
    setLastSubmittedMessage(message);

    try {
      const answer = await sendChatMessage(message);
      setMessages((currentMessages) => [
        ...currentMessages,
        { id: crypto.randomUUID(), content: answer, sender: "assistant" },
      ]);
    } catch (error) {
      setErrorMessage(
        error instanceof Error ? error.message : "Unable to send your message.",
      );
    } finally {
      setIsLoading(false);
    }
  }

  function submitMessage(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const message = draft.trim();

    if (!message || isLoading) {
      return;
    }

    setMessages((currentMessages) => [
      ...currentMessages,
      { id: crypto.randomUUID(), content: message, sender: "user" },
    ]);
    setDraft("");
    void attemptMessage(message);
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
            onClick={() => {
              clearChat();
              updateOpenState(false);
            }}
            aria-label="Close banking assistant"
            title="Close"
          >
            <X aria-hidden="true" size={18} />
          </button>
        </div>
      </header>
      <div className="chat-widget-messages" aria-live="polite">
        {messages.map((message) => (
          <div
            className={`chat-widget-message chat-widget-message--${message.sender}`}
            key={message.id}
          >
            {message.content}
          </div>
        ))}
        {isLoading && (
          <div className="chat-widget-loading" role="status">
            <LoaderCircle aria-hidden="true" size={17} />
            <span>Thinking</span>
          </div>
        )}
        {errorMessage && (
          <div className="chat-widget-error" role="alert">
            <span>{errorMessage}</span>
            <button
              type="button"
              onClick={() => {
                if (lastSubmittedMessage) {
                  void attemptMessage(lastSubmittedMessage);
                }
              }}
              disabled={!lastSubmittedMessage || isLoading}
              aria-label="Retry message"
              title="Retry message"
            >
              <RefreshCw aria-hidden="true" size={15} />
            </button>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <form className="chat-widget-form" onSubmit={submitMessage}>
        <label className="chat-widget-input-label" htmlFor="chat-widget-input">
          Message the assistant
        </label>
        <div className="chat-widget-input-row">
          <input
            id="chat-widget-input"
            value={draft}
            maxLength={2000}
            onChange={(event) => setDraft(event.target.value)}
            placeholder="Ask a banking question"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!draft.trim() || isLoading}
            aria-label="Send message"
            title="Send message"
          >
            <Send aria-hidden="true" size={17} />
          </button>
        </div>
      </form>
    </aside>
  );
}

export default ChatWidget;
