import { useState, type SubmitEvent } from "react";
import { useNavigate } from "react-router";

import { login } from "../api/authClient";
import { GoogleLoginButton } from "../components/GoogleLoginButton";
import { googleLogin } from "../api/authClient";
import { saveTokens } from "../auth/tokenStorage";

export function LoginPage() {
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

    const tokens = await googleLogin({
      id_token: idToken,
    });

    saveTokens(tokens);
    navigate("/dashboard");
  }

  return (
    <main className="login-page">
      <form className="login-form" onSubmit={handleSubmit}>
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
          onError={setError}
        />
        {error && <p>{error}</p>}
      </form>
    </main>
  );
}
