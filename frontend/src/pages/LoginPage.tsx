import { useState, type SubmitEvent } from "react";
import { Link, useNavigate } from "react-router";
// "react-router-dom" extends "react-router" with browser specific tools

import { login } from "../api/authClient";
import { GoogleLoginButton } from "../components/GoogleLoginButton";
import { googleLogin } from "../api/authClient";
import { saveTokens } from "../auth/tokenStorage";

export default function LoginPage() {
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(
    event: SubmitEvent<HTMLFormElement>,
  ): Promise<void> {
    event.preventDefault();

    setIsSubmitting(true);
    setError("");

    try {
      const tokens = await login({
        username,
        password,
      });

      saveTokens(tokens);

      navigate("/dashboard");
    } catch (error) {
      if (error instanceof Error) {
        setError(error.message);
      } else {
        setError("Login failed.");
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleGoogleCredential(idToken: string) {
    setError("");
    setIsSubmitting(true);

    try {
      const tokens = await googleLogin({
        id_token: idToken,
      });

      saveTokens(tokens);
      navigate("/dashboard");
    } catch (error) {
      setError(error instanceof Error ? error.message : "Google login failed.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="auth-page">
      <form className="auth-form" onSubmit={handleSubmit}>
        <h1>Sign in</h1>

        <label htmlFor="username">Username</label>

        <input
          id="username"
          type="text"
          value={username}
          onChange={(event) => setUsername(event.target.value)}
          autoComplete="username"
          required
        />

        <label htmlFor="password">Password</label>

        <input
          id="password"
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          autoComplete="current-password"
          required
        />

        {error && <p className="error-message">{error}</p>}

        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Signing in..." : "Sign in"}
        </button>

        <GoogleLoginButton
          onCredential={handleGoogleCredential}
          onError={() => setError("Google login failed.")}
        />

        <p>
          Don&apos;t have an account? <Link to="/register">Create one</Link>
        </p>
      </form>
    </main>
  );
}
