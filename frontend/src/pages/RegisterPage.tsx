import { useState, type SubmitEvent } from "react";
import { Link, useNavigate } from "react-router";

import { register } from "../api/authClient";
import { saveTokens } from "../auth/tokenStorage";
import { isAllowedEmail } from "../auth/emailValidation";

export default function RegisterPage() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [isSubmitting, setIsSubmitting] = useState(false); // for disabling the submit button
  const [error, setError] = useState(""); // for displaying the error message

  async function handleSubmit(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    if (!isAllowedEmail(email)) {
      setError(
        "Please use your @informationtechconsultants.co.uk email address.",
      );
      return
    }
    setIsSubmitting(true);
    try {
      const tokens = await register({
        email,
        password,
      });

      saveTokens(tokens); // could do this in the api?

      navigate("/dashboard", { replace: true }); // for the browser back button
    } catch (error) {
      setError(error instanceof Error ? error.message : "Registration failed.");
    } finally {
      setIsSubmitting(false);
    }
  }
  return (
    <main className="auth-page">
      <form className="auth-form" onSubmit={handleSubmit}>
        <h1>Create account</h1>

        <label htmlFor="username">ITC Email</label>

        <input
          id="email"
          type="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          autoComplete="email"
          required
        />

        <label htmlFor="password">Password</label>

        <input
          id="password"
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          autoComplete="new-password"
          required
        />

        {error && (
          <p className="error-message" role="alert">
            {error}
          </p>
        )}

        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Creating account..." : "Create account"}
        </button>

        <p>
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </form>
    </main>
  );
}
