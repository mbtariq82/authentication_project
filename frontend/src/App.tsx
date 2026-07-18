import "./App.css";

function App() {
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
              <input id="email" type="email" placeholder="you@example.com" />
            </div>

            <div className="form-field">
              <div className="password-label-row">
                <label htmlFor="password">Password</label>
                <button type="button" className="show-password-button">
                  Show
                </button>
              </div>

              <input
                id="password"
                type="password"
                placeholder="Enter your password"
              />
            </div>

            <div className="form-options">
              <label className="remember-option">
                <input type="checkbox" />
                <span>Remember me</span>
              </label>

              <a href="#">Forgot password?</a>
            </div>

            <button type="submit" className="sign-in-button">
              Sign in
            </button>
          </form>
        </div>
      </section>
    </main>
  );
}

export default App;
