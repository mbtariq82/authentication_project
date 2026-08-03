import { useState, type SubmitEvent } from "react";
import { Link, useNavigate } from "react-router";

import useCreateConsultant from "../hooks/useCreateConsultant";
import useUnassignedUsers from "../hooks/useUnassignedUsers";

import type { Batch, PlacementStatus } from "../types/consultant";

export default function AddConsultantPage() {
  const [userId, setUserId] = useState("");
  const [batch, setBatch] = useState<Batch>("PYTHON");
  const [placementStatus, setPlacementStatus] =
    useState<PlacementStatus>("ONBOARDING");
  const [client, setClient] = useState("");

  const navigate = useNavigate();
  const usersQuery = useUnassignedUsers();
  const createConsultantMutation = useCreateConsultant();

  async function handleSubmit(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!userId) {
      return;
    }

    await createConsultantMutation.mutateAsync({
      user_id: Number(userId),
      batch,
      placement_status: placementStatus,
      client: client.trim() || null,
    });

    navigate("/admin/consultants");
  }

  if (usersQuery.isPending) {
    return <p>Loading users...</p>;
  }

  if (usersQuery.isError) {
    return <p>{usersQuery.error.message}</p>;
  }

  return (
    <main className="add-consultant-page">
      <header className="add-consultant-header">
        <div>
          <h1>Add consultant</h1>
          <p>Assign an existing user to a consultant profile.</p>
        </div>

        <Link className="add-consultant-back-link" to="/admin/consultants">
          Back to consultants
        </Link>
      </header>

      {usersQuery.data.length === 0 ? (
        <section className="add-consultant-empty">
          <h2>No available users</h2>
          <p>Every registered user already has a consultant profile.</p>
        </section>
      ) : (
        <form className="add-consultant-form" onSubmit={handleSubmit}>
          <div className="add-consultant-field">
            <label htmlFor="user">User</label>
            <select
              id="user"
              value={userId}
              onChange={(event) => setUserId(event.target.value)}
              required
            >
              <option value="">Select a user</option>

              {usersQuery.data.map((user) => (
                <option key={user.id} value={user.id}>
                  {user.first_name} {user.last_name} — {user.email}
                </option>
              ))}
            </select>
          </div>

          <div className="add-consultant-field">
            <label htmlFor="batch">Batch</label>
            <select
              id="batch"
              value={batch}
              onChange={(event) => setBatch(event.target.value as Batch)}
            >
              <option value="PYTHON">Python</option>
              <option value="JAVA">Java</option>
              <option value="DATA">Data</option>
              <option value="ANDROID">Android</option>
            </select>
          </div>

          <div className="add-consultant-field">
            <label htmlFor="placement-status">Placement status</label>
            <select
              id="placement-status"
              value={placementStatus}
              onChange={(event) =>
                setPlacementStatus(event.target.value as PlacementStatus)
              }
            >
              <option value="ONBOARDING">Onboarding</option>
              <option value="TRAINING">Training</option>
              <option value="AVAILABLE">Available</option>
              <option value="PLACED">Placed</option>
              <option value="ENDING_SOON">Ending soon</option>
            </select>
          </div>

          <div className="add-consultant-field">
            <label htmlFor="client">Client</label>
            <input
              id="client"
              value={client}
              onChange={(event) => setClient(event.target.value)}
              placeholder="Optional"
            />
          </div>

          {createConsultantMutation.isError && (
            <p className="add-consultant-error">
              {createConsultantMutation.error.message}
            </p>
          )}

          <button
            className="add-consultant-submit"
            type="submit"
            disabled={!userId || createConsultantMutation.isPending}
          >
            {createConsultantMutation.isPending
              ? "Adding..."
              : "Add consultant"}
          </button>
        </form>
      )}
    </main>
  );
}
