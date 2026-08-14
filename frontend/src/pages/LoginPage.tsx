import { useState, type SubmitEvent } from "react";
import { Link, useNavigate } from "react-router";

import GoogleLoginButton from "../components/GoogleLoginButton";
import AuthShell from "../components/AuthShell";
import { login } from "../api/authClient";
import { googleLogin } from "../api/authClient";
import { getUserProfile } from "../api/userClient";

import { saveTokens } from "../auth/tokenStorage";

export default function LoginPage() {
  const navigate = useNavigate();
  const isGoogleLoginConfigured = Boolean(
    import.meta.env.VITE_GOOGLE_CLIENT_ID,
  );

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(
    event: SubmitEvent<HTMLFormElement>,
  ): Promise<void> {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);
    try {
      const tokens = await login({
        email,
        password,
      });
      saveTokens(tokens);
      const user = await getUserProfile();

      if (user.role === "ADMIN") {
        navigate("/admin/dashboard");
        return;
      }
      navigate("/account", { replace: true });
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
      const user = await getUserProfile();
      if (user.role === "ADMIN") {
        navigate("/admin/dashboard");
        return;
      }
      navigate("/account", { replace: true });
    } catch (error) {
      setError(error instanceof Error ? error.message : "Google login failed.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <AuthShell>
      <form className="auth-form" onSubmit={handleSubmit} aria-busy={isSubmitting}>
        <header className="auth-form-heading">
          <p className="auth-eyebrow">Secure customer access</p>
          <h1>Welcome back</h1>
          <p>Sign in to view and manage your Demo Bank account.</p>
        </header>

        <div className="auth-field">
          <label htmlFor="email">Email address</label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            autoComplete="email"
            autoCapitalize="none"
            required
          />
        </div>

        <div className="auth-field">
          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            autoComplete="current-password"
            required
          />
        </div>

        {error && (
          <p className="error-message" role="alert">
            {error}
          </p>
        )}

        <button className="auth-primary-action" type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Signing in..." : "Sign in"}
        </button>

        {isGoogleLoginConfigured && (
          <>
            <div className="auth-divider">
              <span>or continue with</span>
            </div>

            <div className="google-login-wrapper">
              <GoogleLoginButton
                onCredential={handleGoogleCredential}
                onError={() => setError("Google login failed.")}
              />
            </div>
          </>
        )}

        <p className="auth-form-footer">
          New to Demo Bank? <Link to="/register">Open an account</Link>
        </p>
      </form>
    </AuthShell>
  );
}
