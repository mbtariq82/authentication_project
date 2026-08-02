import { useState } from "react";
import { Link, useNavigate } from "react-router";
import { useQueryClient } from "@tanstack/react-query";

import { logout } from "../api/authClient";
import { clearTokens } from "../auth/tokenStorage";

import useConsultants from "../hooks/useConsultants";

export default function ConsultantsPage() {
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const { data, error, isPending, isError, isFetching, isPlaceholderData } =
    useConsultants(page, pageSize);

  if (isPending) {
    return <p>Loading consultants...</p>;
  }
  if (isError) {
    return <p>{error.message}</p>;
  }
  const totalPages = Math.ceil(data.total / pageSize);

  const [isLoggingOut, setIsLoggingOut] = useState(false);

  const queryClient = useQueryClient();
  const navigate = useNavigate();

  async function handleLogout() {
    setIsLoggingOut(true);
    try {
      await logout();
    } catch (error) {
      console.error("Backend logout failed", error);
    } finally {
      await queryClient.cancelQueries();
      clearTokens();
      navigate("/login", { replace: true });
    }
  }

  return (
    <main className="consultants-page">
      <header className="header">
        <h1>All Consultants</h1>
        <Link className="consultants-link" to="/admin/consultants">
          Consultants
        </Link>
        <button
          className="logout-button"
          onClick={handleLogout}
          disabled={isLoggingOut}
        >
          Logout
        </button>
        {isFetching && <span>Refreshing...</span>}
      </header>

      <table className="consultants-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Batch</th>
            <th>Status</th>
            <th>Client</th>
          </tr>
        </thead>

        <tbody>
          {data.items.map((consultant) => (
            <tr key={consultant.id}>
              <td>
                {consultant.first_name} {consultant.last_name}
              </td>
              <td>{consultant.email}</td>
              <td>{consultant.batch}</td>
              <td>{consultant.placement_status}</td>
              <td>{consultant.client ?? "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="consultants-pagination">
        <button
          onClick={() => setPage((current) => current - 1)}
          disabled={page === 1 || isPlaceholderData}
        >
          Previous
        </button>

        <span>
          Page {page} of {totalPages}
        </span>

        <button
          onClick={() => setPage((current) => current + 1)}
          disabled={page >= totalPages || isPlaceholderData}
        >
          Next
        </button>

        <select
          value={pageSize}
          onChange={(event) => {
            setPageSize(Number(event.target.value));
            setPage(1);
          }}
        >
          <option value={20}>20</option>
          <option value={50}>50</option>
          <option value={100}>100</option>
          <option value={200}>200</option>
          <option value={2000}>2000</option>
        </select>
      </div>
    </main>
  );
}
