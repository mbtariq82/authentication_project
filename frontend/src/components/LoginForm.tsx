import { useState } from "react";
import type { SyntheticEvent } from "react";
import { login } from "../api/authClient";
import { saveTokens } from "../auth/tokenStorage";

type LoginStatus = "idle" | "loading" | "success" | "error";
type LoginFormProps = {
  onLoginSuccess: (email: string) => void;
};

function LoginForm({ onLoginSuccess }: LoginFormProps) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [loginStatus, setLoginStatus] = useState<LoginStatus>("idle");
  const [errorMessage, setErrorMessage] = useState("");

  async function handleSubmit(
    event: SyntheticEvent<HTMLFormElement, SubmitEvent>,
  ) {
    event.preventDefault();

    setLoginStatus("loading");
    setErrorMessage("");

    try {
      const tokens = await login({
        username,
        password,
      });

      saveTokens(tokens);

      setLoginStatus("success");
      onLoginSuccess(username);
    } catch (error) {
      setLoginStatus("error");

      if (error instanceof Error) {
        setErrorMessage(error.message);
      } else {
        setErrorMessage("Something went wrong.");
      }
    }
  }

  return (
    <form className="login-form" onSubmit={handleSubmit}>
      <div className="form-field">
        <label htmlFor="username">Username</label>
        <input
          id="username"
          name="username"
          type="text"
          value={username}
          onChange={(event) => setUsername(event.target.value)}
          autoComplete="username"
          required
        />
      </div>

      <div className="form-field">
        <div className="password-label-row">
          <label htmlFor="password">Password</label>
          <button
            type="button"
            className="show-password-button"
            onClick={() => setShowPassword((current) => !current)}
          >
            {showPassword ? "Hide" : "Show"}
          </button>
        </div>

        <input
          id="password"
          name="password"
          type={showPassword ? "text" : "password"}
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          autoComplete="current-password"
          required
        />
      </div>

      <div className="form-options">
        <label className="remember-option">
          <input
            type="checkbox"
            checked={rememberMe}
            onChange={(event) => setRememberMe(event.target.checked)}
          />
          <span>Remember me</span>
        </label>

        <a href="#">Forgot password?</a>
      </div>

      <button
        type="submit"
        className="sign-in-button"
        disabled={loginStatus === "loading"}
      >
        {loginStatus === "loading" ? "Signing in..." : "Sign in"}
      </button>

      {loginStatus === "success" && (
        <p className="login-message login-message-success">Login successful.</p>
      )}
      {loginStatus === "error" && (
        <p className="login-message login-message-error">{errorMessage}</p>
      )}

      <div className="auth-divider">
        <span>Or continue with</span>
      </div>

      <div className="alternative-login-options">
        <button type="button" className="alternative-login-button">
          <span className="auth-icon">◉</span>
          Sign in with a passkey
        </button>

        <div className="oauth-button-row">
          <button type="button" className="alternative-login-button">
            <span className="auth-icon">G</span>
            Google
          </button>

          <button type="button" className="alternative-login-button">
            <span className="auth-icon">⌘</span>
            GitHub
          </button>
        </div>
      </div>

      <p className="register-link">
        Don&apos;t have an account? <a href="#">Create account</a>
      </p>
    </form>
  );
}

export default LoginForm;
