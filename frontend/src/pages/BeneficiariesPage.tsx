import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router";

import { logout } from "../api/authClient";
import { clearTokens } from "../auth/tokenStorage";
import { useBeneficiaries } from "../hooks/useBeneficiaries";
import {
  useCreateBeneficiary,
  useDeactivateBeneficiary,
  useUpdateBeneficiary,
} from "../hooks/useBeneficiaryMutations";
import type {
  CreateBeneficiaryRequest,
  UpdateBeneficiaryRequest,
} from "../types/beneficiary";

const emptyForm: CreateBeneficiaryRequest = {
  name: "",
  account_number: "",
  sort_code: "",
  bank_name: "",
  reference: "",
};

export default function BeneficiariesPage() {
  const navigate = useNavigate();
  const beneficiariesQuery = useBeneficiaries();
  const createMutation = useCreateBeneficiary();
  const updateMutation = useUpdateBeneficiary();
  const deactivateMutation = useDeactivateBeneficiary();

  const [form, setForm] = useState<CreateBeneficiaryRequest>(emptyForm);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [message, setMessage] = useState("");

  async function handleLogout() {
    try {
      await logout();
    } finally {
      clearTokens();
      navigate("/login", { replace: true });
    }
  }

  function updateField(field: keyof CreateBeneficiaryRequest, value: string) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  function startEditing(id: number) {
    const beneficiary = beneficiariesQuery.data?.find((item) => item.id === id);
    if (!beneficiary) return;
    setEditingId(id);
    setForm({
      name: beneficiary.name,
      account_number: beneficiary.account_number,
      sort_code: beneficiary.sort_code,
      bank_name: beneficiary.bank_name,
      reference: beneficiary.reference ?? "",
    });
    setMessage("");
  }

  function resetForm(clearMessage = true) {
    setEditingId(null);
    setForm(emptyForm);
    if (clearMessage) setMessage("");
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage("");
    try {
      if (editingId !== null) {
        const request: UpdateBeneficiaryRequest = form;
        await updateMutation.mutateAsync({ beneficiaryId: editingId, request });
        setMessage("Beneficiary updated.");
      } else {
        await createMutation.mutateAsync(form);
        setMessage("Beneficiary added.");
      }
      resetForm(false);
    } catch (error) {
      setMessage(
        error instanceof Error ? error.message : "Unable to save beneficiary.",
      );
    }
  }

  async function handleDeactivate(id: number) {
    setMessage("");
    try {
      await deactivateMutation.mutateAsync(id);
      setMessage("Beneficiary deactivated.");
      if (editingId === id) resetForm();
    } catch (error) {
      setMessage(
        error instanceof Error
          ? error.message
          : "Unable to deactivate beneficiary.",
      );
    }
  }

  const isSaving = createMutation.isPending || updateMutation.isPending;
  const isLoading = beneficiariesQuery.isLoading;

  return (
    <main className="customer-home">
      <header className="customer-header">
        <Link className="customer-brand-lockup" to="/account">
          <span className="auth-brand-mark" aria-hidden="true">
            D
          </span>
          <span>Demo Bank</span>
        </Link>
        <nav className="customer-nav" aria-label="Customer navigation">
          <Link to="/account">Account</Link>
          <Link className="customer-nav-active" to="/beneficiaries">
            Beneficiaries
          </Link>
          <Link to="/transactions">Transactions</Link>
          <button
            className="customer-logout"
            type="button"
            onClick={handleLogout}
          >
            Sign out
          </button>
        </nav>
      </header>

      <section className="customer-content beneficiaries-page">
        <div className="customer-welcome">
          <p className="auth-eyebrow">Payments</p>
          <h1>Beneficiaries</h1>
          <p>Manage the people and businesses you can transfer money to.</p>
        </div>

        <div className="beneficiaries-layout">
          <section
            className="beneficiary-panel"
            aria-labelledby="beneficiary-form-title"
          >
            <header>
              <p className="customer-card-label">
                {editingId ? "Edit details" : "New beneficiary"}
              </p>
              <h2 id="beneficiary-form-title">
                {editingId ? "Update beneficiary" : "Add a beneficiary"}
              </h2>
            </header>
            <form className="beneficiary-form" onSubmit={handleSubmit}>
              {(
                [
                  "name",
                  "account_number",
                  "sort_code",
                  "bank_name",
                  "reference",
                ] as const
              ).map((field) => (
                <label key={field}>
                  {field === "account_number"
                    ? "Account number"
                    : field === "sort_code"
                      ? "Sort code"
                      : field === "bank_name"
                        ? "Bank name"
                        : field === "reference"
                          ? "Reference (optional)"
                          : "Name"}
                  <input
                    value={form[field] ?? ""}
                    onChange={(event) => updateField(field, event.target.value)}
                    required={field !== "reference"}
                    maxLength={
                      field === "name"
                        ? 150
                        : field === "account_number"
                          ? 50
                          : field === "sort_code"
                            ? 20
                            : field === "bank_name"
                              ? 150
                              : 255
                    }
                  />
                </label>
              ))}
              {message && (
                <p className="beneficiary-message" role="status">
                  {message}
                </p>
              )}
              <div className="beneficiary-form-actions">
                <button
                  className="auth-primary-action"
                  type="submit"
                  disabled={isSaving}
                >
                  {isSaving
                    ? "Saving..."
                    : editingId
                      ? "Save changes"
                      : "Add beneficiary"}
                </button>
                {editingId && (
                  <button
                    className="secondary-action"
                    type="button"
                    onClick={resetForm}
                  >
                    Cancel
                  </button>
                )}
              </div>
            </form>
          </section>

          <section
            className="beneficiary-panel"
            aria-labelledby="beneficiary-list-title"
          >
            <header className="beneficiary-list-heading">
              <div>
                <p className="customer-card-label">Saved recipients</p>
                <h2 id="beneficiary-list-title">Your beneficiaries</h2>
              </div>
              <span className="customer-status">
                {beneficiariesQuery.data?.length ?? 0} active
              </span>
            </header>
            {isLoading && <p role="status">Loading beneficiaries...</p>}
            {beneficiariesQuery.isError && (
              <p className="beneficiary-error">
                {beneficiariesQuery.error.message}
              </p>
            )}
            {!isLoading &&
              !beneficiariesQuery.isError &&
              beneficiariesQuery.data?.length === 0 && (
                <p className="beneficiary-empty">No beneficiaries added yet.</p>
              )}
            <div className="beneficiary-list">
              {beneficiariesQuery.data?.map((beneficiary) => (
                <article className="beneficiary-item" key={beneficiary.id}>
                  <div>
                    <h3>{beneficiary.name}</h3>
                    <p>
                      {beneficiary.bank_name} · {beneficiary.sort_code}
                    </p>
                    <p>Account ending {beneficiary.account_number.slice(-4)}</p>
                    {beneficiary.reference && (
                      <small>{beneficiary.reference}</small>
                    )}
                  </div>
                  <div className="beneficiary-item-actions">
                    <button
                      className="secondary-action"
                      type="button"
                      onClick={() => startEditing(beneficiary.id)}
                    >
                      Edit
                    </button>
                    <button
                      className="danger-action"
                      type="button"
                      disabled={deactivateMutation.isPending}
                      onClick={() => void handleDeactivate(beneficiary.id)}
                    >
                      Deactivate
                    </button>
                  </div>
                </article>
              ))}
            </div>
          </section>
        </div>
      </section>
    </main>
  );
}
