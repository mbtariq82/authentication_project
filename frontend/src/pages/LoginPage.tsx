import { useNavigate } from "react-router";
import LoginForm from "../components/LoginForm";

function LoginPage() {
  const navigate = useNavigate();

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

          <LoginForm
            onLoginSuccess={() => navigate("/dashboard", { replace: true })}
          />
        </div>
      </section>
    </main>
  );
}

export default LoginPage;
