import { useState, type SubmitEvent } from "react";
import { Link, useNavigate } from "react-router";
// "react-router-dom" extends "react-router" with browser specific tools

import GoogleLoginButton from "../components/GoogleLoginButton";

//import useLogin from "../hooks/useLogin";
import { login } from "../api/authClient";
import { googleLogin } from "../api/authClient";
import { getUserProfile } from "../api/userClient";

import { saveTokens } from "../auth/tokenStorage";
import { isAllowedEmail } from "../auth/emailValidation";

export default function LoginPage() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [isSubmitting, setIsSubmitting] = useState(false); // for disabling the submit button
  const [error, setError] = useState(""); // for displaying the error message

  //const { login, isLoading, error } = useLogin();

  async function handleSubmit(
    event: SubmitEvent<HTMLFormElement>,
  ): Promise<void> {
    event.preventDefault();
    setError("");
    if (!isAllowedEmail(email)) {
      setError(
        "Please use your @informationtechconsultants.co.uk email address.",
      );
      return;
    }
    setIsSubmitting(true);
    try {
      const tokens = await login({
        email,
        password,
      });
      saveTokens(tokens); // could do this in api?
      const user = await getUserProfile();

      console.log("Current user:", user);
      console.log("Current role:", user.role);

      if (user.role === "ADMIN") {
        navigate("/admin/dashboard");
        return;
      }
      navigate("/profile");
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
      navigate("/profile");
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
          New to ITC? <Link to="/register">Register here</Link>
        </p>
      </form>
    </main>
  );
}
