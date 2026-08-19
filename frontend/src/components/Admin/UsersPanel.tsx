import { useEffect, useState } from "react";
import type { AdminUser, UserStatus } from "../../types/admin";
import { fetchUsers, updateUserStatus } from "../../api/adminApi";
import StatusBadge from "./StatusBadge";

const FILTERS: {
  key: UserStatus | "all";
  label: string;
}[] = [
  { key: "all", label: "All" },
  { key: "PENDING", label: "Pending" },
  { key: "APPROVED", label: "Approved" },
  { key: "REJECTED", label: "Rejected" },
];

export default function UsersPanel() {
  const [users, setUsers] = useState<AdminUser[]>([]);

  const [filter, setFilter] = useState<UserStatus | "all">("all");

  const [loading, setLoading] = useState(true);

  const [error, setError] = useState<string | null>(null);

  const [actingOn, setActingOn] = useState<number | null>(null);

  // Detail modal
  const [selectedUser, setSelectedUser] = useState<AdminUser | null>(null);

  // Edit modal
  const [editingUser, setEditingUser] = useState<AdminUser | null>(null);

  // Reject modal
  const [rejectingUser, setRejectingUser] = useState<AdminUser | null>(null);

  const [rejectionReason, setRejectionReason] = useState("");

  async function loadUsers() {
    setLoading(true);
    setError(null);

    try {
      const data = await fetchUsers();
      setUsers(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load users");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadUsers();
  }, []);

  async function handleApprove(userId: number) {
    setActingOn(userId);
    setError(null);

    try {
      const updated = await updateUserStatus(userId, "APPROVED");

      setUsers((prev) =>
        prev.map((user) => (user.id === userId ? updated : user)),
      );

      setEditingUser(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to approve user");
    } finally {
      setActingOn(null);
    }
  }

  function openRejectModal(user: AdminUser) {
    setRejectingUser(user);
    setEditingUser(null);
    setRejectionReason("");
    setError(null);
  }

  async function handleReject() {
    if (!rejectingUser) {
      return;
    }

    if (!rejectionReason.trim()) {
      setError("Rejection reason is required.");
      return;
    }

    setActingOn(rejectingUser.id);
    setError(null);

    try {
      const updated = await updateUserStatus(
        rejectingUser.id,
        "REJECTED",
        rejectionReason.trim(),
      );

      setUsers((prev) =>
        prev.map((user) => (user.id === rejectingUser.id ? updated : user)),
      );

      setRejectingUser(null);
      setRejectionReason("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to reject user");
    } finally {
      setActingOn(null);
    }
  }

  const visibleUsers =
    filter === "all"
      ? users
      : users.filter((user) => user.user_status === filter);

  return (
    <div className="panel">
      {/* HEADER */}

      <div className="panel-header">
        <div className="panel-title">User applications</div>

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

      {loading && <div className="panel-loading">Loading users...</div>}

      {/* ERROR */}

      {error && <div className="panel-error">{error}</div>}

      {/* USERS TABLE */}

      {!loading && (
        <>
          {visibleUsers.length === 0 ? (
            <div className="panel-empty">No users match this filter.</div>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>Customer</th>
                  <th>Email</th>
                  <th>Role</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>
                {visibleUsers.map((user) => {
                  const fullName = `${user.first_name ?? ""} ${
                    user.last_name ?? ""
                  }`.trim();

                  const initials = `${user.first_name?.[0] ?? ""}${
                    user.last_name?.[0] ?? ""
                  }`;

                  return (
                    <tr key={user.id}>
                      {/* CUSTOMER */}

                      <td>
                        <div className="customer">
                          <div className="customer-avatar">
                            {initials || "NA"}
                          </div>

                          <div className="customer-name">
                            {fullName || "Unknown user"}
                          </div>
                        </div>
                      </td>

                      {/* EMAIL */}

                      <td>{user.email}</td>

                      {/* ROLE */}

                      <td>{user.role}</td>

                      {/* STATUS */}

                      <td>
                        <StatusBadge status={user.user_status} />
                      </td>

                      {/* ACTIONS */}

                      <td>
                        <div className="actions">
                          {/* DETAIL */}

                          <button
                            className="btn detail-btn"
                            type="button"
                            onClick={() => setSelectedUser(user)}
                          >
                            👁 Detail
                          </button>

                          {/* EDIT */}

                          <button
                            className="btn edit-btn"
                            type="button"
                            onClick={() => {
                              setEditingUser(user);
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
            Showing {visibleUsers.length} of {users.length} users
          </div>
        </>
      )}

      {/* ==========================
          USER DETAIL MODAL
      ========================== */}

      {selectedUser && (
        <div className="modal-overlay">
          <div className="admin-modal">
            <div className="modal-header">
              <h2>User Details</h2>

              <button
                type="button"
                className="modal-close"
                onClick={() => setSelectedUser(null)}
              >
                ×
              </button>
            </div>

            <div className="user-details-grid">
              <div>
                <strong>Name</strong>

                <p>
                  {selectedUser.first_name} {selectedUser.last_name}
                </p>
              </div>

              <div>
                <strong>Email</strong>

                <p>{selectedUser.email}</p>
              </div>

              <div>
                <strong>Role</strong>

                <p>{selectedUser.role}</p>
              </div>

              <div>
                <strong>Status</strong>

                <p>{selectedUser.user_status}</p>
              </div>

              <div>
                <strong>Date of birth</strong>

                <p>{selectedUser.dob ?? "—"}</p>
              </div>

              <div>
                <strong>Mobile</strong>

                <p>{selectedUser.mobile ?? "—"}</p>
              </div>

              <div>
                <strong>Address</strong>

                <p>{selectedUser.address_line ?? "—"}</p>
              </div>

              <div>
                <strong>City</strong>

                <p>{selectedUser.city ?? "—"}</p>
              </div>

              <div>
                <strong>County</strong>

                <p>{selectedUser.county ?? "—"}</p>
              </div>

              <div>
                <strong>Postcode</strong>

                <p>{selectedUser.postcode ?? "—"}</p>
              </div>

              {selectedUser.rejection_reason && (
                <div>
                  <strong>Rejection reason</strong>

                  <p>{selectedUser.rejection_reason}</p>
                </div>
              )}
            </div>

            <div className="modal-actions">
              <button
                className="btn"
                type="button"
                onClick={() => setSelectedUser(null)}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ==========================
          EDIT USER MODAL
      ========================== */}

      {editingUser && (
        <div className="modal-overlay">
          <div className="admin-modal">
            <div className="modal-header">
              <h2>Edit User</h2>

              <button
                type="button"
                className="modal-close"
                onClick={() => setEditingUser(null)}
              >
                ×
              </button>
            </div>

            <div className="edit-user-info">
              <p>
                <strong>User:</strong> {editingUser.first_name}{" "}
                {editingUser.last_name}
              </p>

              <p>
                <strong>Email:</strong> {editingUser.email}
              </p>

              <p>
                <strong>Current Status:</strong> {editingUser.user_status}
              </p>
            </div>

            {/* PENDING USER ACTIONS */}

            {editingUser.user_status === "PENDING" && (
              <div className="modal-actions">
                <button
                  className="btn approve"
                  type="button"
                  disabled={actingOn === editingUser.id}
                  onClick={() => handleApprove(editingUser.id)}
                >
                  {actingOn === editingUser.id ? "Approving..." : "Approve"}
                </button>

                <button
                  className="btn reject"
                  type="button"
                  disabled={actingOn === editingUser.id}
                  onClick={() => openRejectModal(editingUser)}
                >
                  Reject
                </button>
              </div>
            )}

            {/* APPROVED USER */}

            {editingUser.user_status === "APPROVED" && (
              <div className="modal-message">
                This user is already approved.
              </div>
            )}

            {/* REJECTED USER */}

            {editingUser.user_status === "REJECTED" && (
              <div className="modal-message">
                <p>This user is rejected.</p>

                {editingUser.rejection_reason && (
                  <p>
                    <strong>Reason:</strong> {editingUser.rejection_reason}
                  </p>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* ==========================
          REJECT USER MODAL
      ========================== */}

      {rejectingUser && (
        <div className="modal-overlay">
          <div className="admin-modal">
            <div className="modal-header">
              <h2>Reject User</h2>

              <button
                type="button"
                className="modal-close"
                onClick={() => {
                  setRejectingUser(null);
                  setRejectionReason("");
                  setError(null);
                }}
              >
                ×
              </button>
            </div>

            <p>
              You are rejecting{" "}
              <strong>
                {rejectingUser.first_name} {rejectingUser.last_name}
              </strong>
              .
            </p>

            <label className="reject-label">Rejection reason</label>

            <textarea
              className="reject-textarea"
              value={rejectionReason}
              onChange={(event) => setRejectionReason(event.target.value)}
              placeholder="Enter reason for rejection"
              rows={4}
            />

            <div className="modal-actions">
              <button
                className="btn"
                type="button"
                onClick={() => {
                  setRejectingUser(null);
                  setRejectionReason("");
                  setError(null);
                }}
              >
                Cancel
              </button>

              <button
                className="btn reject"
                type="button"
                disabled={
                  !rejectionReason.trim() || actingOn === rejectingUser.id
                }
                onClick={handleReject}
              >
                {actingOn === rejectingUser.id ? "Rejecting..." : "Reject User"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
