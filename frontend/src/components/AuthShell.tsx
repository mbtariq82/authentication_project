import type { ReactNode } from "react";

type AuthShellProps = {
  children: ReactNode;
};

export default function AuthShell({ children }: AuthShellProps) {
  return (
    <main className="auth-page">
      <section className="auth-shell" aria-label="Demo Bank customer access">
        <aside className="auth-brand-panel">
          <div className="auth-brand-lockup">
            <span className="auth-brand-mark" aria-hidden="true">
              D
            </span>
            <span>Demo Bank</span>
          </div>

          <div className="auth-brand-content">
            <div className="auth-brand-copy">
              <p className="auth-eyebrow">Banking made uncomplicated</p>
              <h2>Your money, clearly managed.</h2>
              <p>
                A secure demonstration of simple, modern everyday banking.
              </p>
            </div>

            <ul className="auth-benefits" aria-label="Account benefits">
              <li>Protected account access</li>
              <li>Clear balances and activity</li>
              <li>Available whenever you need it</li>
            </ul>
          </div>

          <p className="demo-notice">Demo environment · No real funds</p>
        </aside>

        <div className="auth-card">{children}</div>
      </section>
    </main>
  );
}
