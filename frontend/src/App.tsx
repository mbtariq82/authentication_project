import { useState } from "react";
import "./App.css";

function App() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);

  return (
    <main className="auth-page">
      <section className="product-preview">
        <div className="preview-content">
          <span className="preview-badge">Developer Platform</span>

          <h1>Secure access to your workspace.</h1>

          <p>
            Build, deploy and manage your applications with enterprise-grade
            authentication.
          </p>

          <div className="dashboard-placeholder">Dashboard Preview</div>

          <div className="status-cards">
            <div className="status-card">✓ 99.98% uptime</div>
            <div className="status-card">🔒 OAuth Ready</div>
          </div>
        </div>
      </section>

      <section className="login-panel">
        <div className="login-content">
          <header className="login-header">
            <p className="login-eyebrow">Workspace access</p>

            <h2>Welcome back</h2>

            <p>Enter your details to continue.</p>
          </header>
          <form className="login-form">
            <div className="form-field">
              <label htmlFor="email">Email</label>
              <input
                id="email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
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
                type={showPassword ? "text" : "password"}
                placeholder="Enter your password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
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

            <button type="submit" className="sign-in-button">
              Sign in
            </button>
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
        </div>
      </section>
    </main>
  );
}

export default App;
