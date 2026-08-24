import { useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";

import { askAdminAgent, exportAdminAgentResult } from "../../api/adminAiClient";
import type { AdminAgentAskResponse } from "../../types/admin";

// import "./AdminAiPanel.css";

import "../../styles/AdminAiPanel.css";

interface ConversationEntry extends AdminAgentAskResponse {
  id: string;
}

const SUGGESTED_QUESTIONS = [
  "List of users whose account balance is 0",
  "How many loans are pending approval?",
  "Show cards created in the last 30 days",
  "Which accounts are frozen?",
];

export default function AdminAiPanel() {
  const [question, setQuestion] = useState("");
  const [entries, setEntries] = useState<ConversationEntry[]>([]);
  const [isAsking, setIsAsking] = useState(false);
  const [exportingId, setExportingId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [entries, isAsking]);

  // ==============================
  // ASK
  // ==============================

  async function submitQuestion(value: string) {
    const trimmed = value.trim();

    if (!trimmed || isAsking) {
      return;
    }

    setIsAsking(true);
    setError(null);

    try {
      const result = await askAdminAgent(trimmed);

      const entry: ConversationEntry = {
        ...result,
        id:
          typeof crypto !== "undefined" && "randomUUID" in crypto
            ? crypto.randomUUID()
            : `${Date.now()}`,
      };

      setEntries((previous) => [...previous, entry]);
      setQuestion("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to get an answer.");
    } finally {
      setIsAsking(false);
    }
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    void submitQuestion(question);
  }

  // ==============================
  // EXPORT
  // ==============================

  async function handleExport(entry: ConversationEntry) {
    setExportingId(entry.id);
    setError(null);

    try {
      await exportAdminAgentResult(entry.question);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to export.");
    } finally {
      setExportingId(null);
    }
  }

  return (
    <div className="ai-panel">
      <div className="ai-panel-scroll" ref={scrollRef}>
        {entries.length === 0 && !isAsking && (
          <div className="ai-empty">
            <div className="ai-empty-icon" aria-hidden="true">
              <svg
                width="22"
                height="22"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.8"
              >
                <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z" />
              </svg>
            </div>

            <p className="ai-empty-title">Ask anything about your data</p>
            <p className="ai-empty-subtitle">
              Try one of these, or type your own question below.
            </p>

            <div className="ai-suggestions">
              {SUGGESTED_QUESTIONS.map((suggestion) => (
                <button
                  key={suggestion}
                  type="button"
                  className="ai-suggestion-chip"
                  onClick={() => void submitQuestion(suggestion)}
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}

        {entries.map((entry) => {
          const columns =
            entry.rows.length > 0 ? Object.keys(entry.rows[0]) : [];

          return (
            <div key={entry.id} className="ai-turn">
              <div className="ai-bubble ai-bubble-user">{entry.question}</div>

              <div className="ai-response">
                <div className="ai-response-avatar" aria-hidden="true">
                  <svg
                    width="14"
                    height="14"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                  >
                    <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z" />
                  </svg>
                </div>

                <div className="ai-response-body">
                  <p className="ai-response-text">{entry.answer}</p>

                  {entry.sql_query && (
                    <details className="ai-sql">
                      <summary>View generated SQL</summary>
                      <pre>{entry.sql_query}</pre>
                    </details>
                  )}

                  {entry.rows.length > 0 && (
                    <>
                      <div className="ai-table-wrapper">
                        <table className="ai-table">
                          <thead>
                            <tr>
                              {columns.map((column) => (
                                <th key={column}>{column}</th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {entry.rows.map((row, rowIndex) => (
                              <tr key={rowIndex}>
                                {columns.map((column) => (
                                  <td key={column}>
                                    {row[column] === null ||
                                    row[column] === undefined
                                      ? ""
                                      : String(row[column])}
                                  </td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>

                      <button
                        type="button"
                        className="ai-export-button"
                        onClick={() => void handleExport(entry)}
                        disabled={exportingId === entry.id}
                      >
                        <svg
                          width="14"
                          height="14"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="2"
                        >
                          <path d="M12 3v12m0 0-4-4m4 4 4-4" />
                          <path d="M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2" />
                        </svg>
                        {exportingId === entry.id
                          ? "Exporting..."
                          : "Export to Excel"}
                      </button>
                    </>
                  )}
                </div>
              </div>
            </div>
          );
        })}

        {isAsking && (
          <div className="ai-response ai-response-loading">
            <div className="ai-response-avatar" aria-hidden="true">
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z" />
              </svg>
            </div>
            <div className="ai-typing-dots">
              <span />
              <span />
              <span />
            </div>
          </div>
        )}
      </div>

      {error && <div className="ai-error">{error}</div>}

      <form className="ai-input-bar" onSubmit={handleSubmit}>
        <input
          type="text"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Ask about customers, accounts, loans, or cards"
          disabled={isAsking}
        />
        <button
          type="submit"
          className="ai-send-button"
          disabled={isAsking || !question.trim()}
          aria-label="Ask"
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
          >
            <path d="M22 2 11 13" />
            <path d="M22 2 15 22l-4-9-9-4 20-7z" />
          </svg>
        </button>
      </form>
    </div>
  );
}
