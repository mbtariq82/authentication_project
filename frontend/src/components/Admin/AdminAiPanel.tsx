import { useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";

import {
  approveAdminAction,
  askAdminAgent,
  downloadAdminExcelFile,
  exportAdminAgentResult,
  rejectAdminAction,
} from "../../api/adminAiClient";
import type { AdminAgentAskResponse, ApprovalStatus } from "../../types/admin";

import "../../styles/AdminAiPanel.css";

interface ConversationEntry extends AdminAgentAskResponse {
  id: string;
}

interface ApprovalActionState {
  loading: boolean;
  error: string | null;
}

const SUGGESTED_QUESTIONS = [
  "List of users whose account balance is 0",
  "How many loans are pending approval?",
  "Show cards created in the last 30 days",
  "Which accounts are frozen?",
];

function isPending(status: ApprovalStatus): boolean {
  return status === "PENDING_APPROVAL" || status === "PENDING";
}

function approvalBadgeLabel(status: ApprovalStatus): string {
  switch (status) {
    case "EXECUTED":
      return "Sent";
    case "APPROVED":
      return "Approved";
    case "REJECTED":
      return "Rejected";
    case "FAILED":
      return "Failed";
    default:
      return "Awaiting approval";
  }
}

function approvalBadgeClass(status: ApprovalStatus): string {
  switch (status) {
    case "EXECUTED":
    case "APPROVED":
      return "ai-approval-badge ai-approval-badge-success";
    case "REJECTED":
      return "ai-approval-badge ai-approval-badge-rejected";
    case "FAILED":
      return "ai-approval-badge ai-approval-badge-failed";
    default:
      return "ai-approval-badge ai-approval-badge-pending";
  }
}

export default function AdminAiPanel() {
  const [question, setQuestion] = useState("");
  const [entries, setEntries] = useState<ConversationEntry[]>([]);
  const [isAsking, setIsAsking] = useState(false);
  const [exportingId, setExportingId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Keyed by approval_id, so the email card and instagram card in the
  // same turn (or across turns) each track their own loading/error
  // state independently.
  const [approvalState, setApprovalState] = useState<
    Record<string, ApprovalActionState>
  >({});

  // Lets the admin paste in an image URL for an Instagram draft when
  // automatic image generation failed (image_url came back null).
  const [imageUrlOverrides, setImageUrlOverrides] = useState<
    Record<string, string>
  >({});

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
  // EXPORT (SQL-only results without a pre-generated excel_file)
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

  // ==============================
  // DOWNLOAD (excel_file the backend already generated)
  // ==============================

  async function handleDownloadExcelFile(entry: ConversationEntry) {
    if (!entry.excel_file) {
      return;
    }

    setExportingId(entry.id);
    setError(null);

    try {
      await downloadAdminExcelFile(
        entry.excel_file.download_url,
        entry.excel_file.filename,
      );
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to download report.",
      );
    } finally {
      setExportingId(null);
    }
  }

  // ==============================
  // APPROVE / REJECT (email + instagram)
  // ==============================

  function updateApprovalKind(
    entryId: string,
    kind: "email" | "instagram",
    status: ApprovalStatus,
  ) {
    setEntries((previous) =>
      previous.map((entry) => {
        if (entry.id !== entryId) {
          return entry;
        }

        if (kind === "email" && entry.email) {
          return { ...entry, email: { ...entry.email, status } };
        }

        if (kind === "instagram" && entry.instagram) {
          return { ...entry, instagram: { ...entry.instagram, status } };
        }

        return entry;
      }),
    );
  }

  async function handleApprove(
    entryId: string,
    kind: "email" | "instagram",
    approvalId: string,
    imageUrl?: string,
  ) {
    setApprovalState((previous) => ({
      ...previous,
      [approvalId]: { loading: true, error: null },
    }));

    try {
      const record = await approveAdminAction(approvalId, imageUrl);
      updateApprovalKind(entryId, kind, record.status);

      setApprovalState((previous) => ({
        ...previous,
        [approvalId]: { loading: false, error: null },
      }));
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to approve.";

      setApprovalState((previous) => ({
        ...previous,
        [approvalId]: { loading: false, error: message },
      }));
    }
  }

  async function handleReject(
    entryId: string,
    kind: "email" | "instagram",
    approvalId: string,
  ) {
    setApprovalState((previous) => ({
      ...previous,
      [approvalId]: { loading: true, error: null },
    }));

    try {
      const record = await rejectAdminAction(approvalId);
      updateApprovalKind(entryId, kind, record.status);

      setApprovalState((previous) => ({
        ...previous,
        [approvalId]: { loading: false, error: null },
      }));
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to reject.";

      setApprovalState((previous) => ({
        ...previous,
        [approvalId]: { loading: false, error: message },
      }));
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
                  {entry.answer && (
                    <p className="ai-response-text">{entry.answer}</p>
                  )}

                  {entry.sql_query && (
                    <details className="ai-sql">
                      <summary>View generated SQL</summary>
                      <pre>{entry.sql_query}</pre>
                    </details>
                  )}

                  {entry.rows.length > 0 && (
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
                  )}

                  {/* Excel: prefer the file the backend already built
                      inline; fall back to the old re-run/export path
                      for results that didn't ask for excel_required. */}
                  {entry.excel_file ? (
                    <button
                      type="button"
                      className="ai-export-button"
                      onClick={() => void handleDownloadExcelFile(entry)}
                      disabled={exportingId === entry.id}
                    >
                      <ExportIcon />
                      {exportingId === entry.id
                        ? "Downloading..."
                        : "Download Excel report"}
                    </button>
                  ) : (
                    entry.rows.length > 0 && (
                      <button
                        type="button"
                        className="ai-export-button"
                        onClick={() => void handleExport(entry)}
                        disabled={exportingId === entry.id}
                      >
                        <ExportIcon />
                        {exportingId === entry.id
                          ? "Exporting..."
                          : "Export to Excel"}
                      </button>
                    )
                  )}

                  {/* -------- Email draft -------- */}
                  {entry.email && (
                    <div className="ai-approval-card">
                      <div className="ai-approval-header">
                        <span className="ai-approval-title">Email draft</span>
                        <span
                          className={approvalBadgeClass(entry.email.status)}
                        >
                          {approvalBadgeLabel(entry.email.status)}
                        </span>
                      </div>

                      <div className="ai-approval-field">
                        <span className="ai-approval-label">To</span>
                        <span className="ai-approval-value">
                          {entry.email.recipient_count} recipient
                          {entry.email.recipient_count === 1 ? "" : "s"}
                          {entry.email.recipients.length > 0 &&
                            ` — ${entry.email.recipients.slice(0, 3).join(", ")}${
                              entry.email.recipients.length > 3 ? ", ..." : ""
                            }`}
                        </span>
                      </div>

                      <div className="ai-approval-field">
                        <span className="ai-approval-label">Subject</span>
                        <span className="ai-approval-value">
                          {entry.email.subject}
                        </span>
                      </div>

                      <p className="ai-approval-body-text">
                        {entry.email.body}
                      </p>

                      {isPending(entry.email.status) && (
                        <ApprovalActions
                          approvalId={entry.email.approval_id}
                          state={approvalState[entry.email.approval_id]}
                          onApprove={() =>
                            void handleApprove(
                              entry.id,
                              "email",
                              entry.email!.approval_id,
                            )
                          }
                          onReject={() =>
                            void handleReject(
                              entry.id,
                              "email",
                              entry.email!.approval_id,
                            )
                          }
                        />
                      )}
                    </div>
                  )}

                  {/* -------- Instagram draft -------- */}
                  {entry.instagram && (
                    <div className="ai-approval-card">
                      <div className="ai-approval-header">
                        <span className="ai-approval-title">
                          Instagram draft
                        </span>
                        <span
                          className={approvalBadgeClass(entry.instagram.status)}
                        >
                          {approvalBadgeLabel(entry.instagram.status)}
                        </span>
                      </div>

                      {entry.instagram.image_url ? (
                        <img
                          className="ai-instagram-image"
                          src={entry.instagram.image_url}
                          alt="Generated Instagram post"
                        />
                      ) : (
                        <div className="ai-instagram-image-placeholder">
                          No image was generated. Paste an image URL below
                          before approving.
                        </div>
                      )}

                      <p className="ai-approval-body-text">
                        {entry.instagram.caption}
                      </p>

                      {isPending(entry.instagram.status) && (
                        <>
                          {!entry.instagram.image_url && (
                            <input
                              type="url"
                              className="ai-image-url-input"
                              placeholder="https://..."
                              value={
                                imageUrlOverrides[
                                  entry.instagram.approval_id
                                ] ?? ""
                              }
                              onChange={(event) =>
                                setImageUrlOverrides((previous) => ({
                                  ...previous,
                                  [entry.instagram!.approval_id]:
                                    event.target.value,
                                }))
                              }
                            />
                          )}

                          <ApprovalActions
                            approvalId={entry.instagram.approval_id}
                            state={approvalState[entry.instagram.approval_id]}
                            approveDisabled={
                              !entry.instagram.image_url &&
                              !imageUrlOverrides[
                                entry.instagram.approval_id
                              ]?.trim()
                            }
                            onApprove={() =>
                              void handleApprove(
                                entry.id,
                                "instagram",
                                entry.instagram!.approval_id,
                                entry.instagram!.image_url ??
                                  imageUrlOverrides[
                                    entry.instagram!.approval_id
                                  ],
                              )
                            }
                            onReject={() =>
                              void handleReject(
                                entry.id,
                                "instagram",
                                entry.instagram!.approval_id,
                              )
                            }
                          />
                        </>
                      )}
                    </div>
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
          placeholder="Ask about customers, accounts, loans, and cards — or ask it to draft an email, Excel report, or Instagram post"
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

// ==============================
// Small shared pieces
// ==============================

function ExportIcon() {
  return (
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
  );
}

interface ApprovalActionsProps {
  approvalId: string;
  state?: ApprovalActionState;
  approveDisabled?: boolean;
  onApprove: () => void;
  onReject: () => void;
}

function ApprovalActions({
  state,
  approveDisabled,
  onApprove,
  onReject,
}: ApprovalActionsProps) {
  const loading = state?.loading ?? false;

  return (
    <div className="ai-approval-actions">
      {state?.error && <div className="ai-approval-error">{state.error}</div>}

      <div className="ai-approval-buttons">
        <button
          type="button"
          className="ai-approve-button"
          onClick={onApprove}
          disabled={loading || approveDisabled}
        >
          {loading ? "Working..." : "Approve & send"}
        </button>

        <button
          type="button"
          className="ai-reject-button"
          onClick={onReject}
          disabled={loading}
        >
          Reject
        </button>
      </div>
    </div>
  );
}
