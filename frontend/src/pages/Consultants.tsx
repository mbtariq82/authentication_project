import { useEffect, useState } from "react";

import {
  getConsultants,
  type ConsultantPage,
} from "../api/consultantClient";

const PAGE_SIZE = 20;

export default function ConsultantsPage() {
  const [page, setPage] = useState(1);
  const [consultantPage, setConsultantPage] =
    useState<ConsultantPage | null>(null);

  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let ignoreResult = false;

    async function loadConsultants() {
      setIsLoading(true);
      setError("");

      try {
        const result = await getConsultants({
          page,
          page_size: PAGE_SIZE,
        });

        if (!ignoreResult) {
          setConsultantPage(result);
        }
      } catch (error) {
        if (!ignoreResult) {
          setError(
            error instanceof Error
              ? error.message
              : "Failed to load consultants.",
          );
        }
      } finally {
        if (!ignoreResult) {
          setIsLoading(false);
        }
      }
    }

    void loadConsultants();

    return () => {
      ignoreResult = true;
    };
  }, [page]);

  if (isLoading && !consultantPage) {
    return (
      <main className="consultants-page">
        <p>Loading consultants...</p>
      </main>
    );
  }

  if (error) {
    return (
      <main className="consultants-page">
        <p className="consultants-error">{error}</p>
      </main>
    );
  }

  if (!consultantPage) {
    return null;
  }

  const totalPages = Math.max(consultantPage.total_pages, 1);

  return (
    <main className="consultants-page">
      <header className="consultants-header">
        <div>
          <h1>Consultants</h1>

          <p>
            {consultantPage.total} consultant
            {consultantPage.total === 1 ? "" : "s"}
          </p>
        </div>

        {isLoading && <span>Updating...</span>}
      </header>

      <section className="consultants-table-container">
        <table className="consultants-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Batch</th>
              <th>Placement status</th>
              <th>Client</th>
            </tr>
          </thead>

          <tbody>
            {consultantPage.items.map((consultant) => (
              <tr key={consultant.id}>
                <td>
                  {consultant.first_name} {consultant.last_name}
                </td>

                <td>{consultant.email}</td>
                <td>{consultant.batch}</td>

                <td>
                  {consultant.placement_status.replaceAll("_", " ")}
                </td>

                <td>{consultant.client ?? "—"}</td>
              </tr>
            ))}

            {consultantPage.items.length === 0 && (
              <tr>
                <td colSpan={5} className="consultants-empty">
                  No consultants found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </section>

      <footer className="consultants-pagination">
        <button
          type="button"
          disabled={page === 1 || isLoading}
          onClick={() => setPage((current) => current - 1)}
        >
          Previous
        </button>

        <span>
          Page {consultantPage.page} of {totalPages}
        </span>

        <button
          type="button"
          disabled={page >= totalPages || isLoading}
          onClick={() => setPage((current) => current + 1)}
        >
          Next
        </button>
      </footer>
    </main>
  );
}



