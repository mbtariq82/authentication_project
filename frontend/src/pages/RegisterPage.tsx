import { useState, type SubmitEvent } from "react";
import { Link, useNavigate } from "react-router";

import { register } from "../api/authClient";
import { saveTokens } from "../auth/tokenStorage";
import AuthShell from "../components/AuthShell";

const MAX_PROFILE_IMAGE_BYTES = 5 * 1024 * 1024;

function isStrongPassword(password: string): boolean {
  return (
    password.length >= 12 &&
    /[a-z]/.test(password) &&
    /[A-Z]/.test(password) &&
    /\d/.test(password) &&
    /[^A-Za-z0-9\s]/.test(password)
  );
}

const passwordChecks = [
  { label: "12+ characters", test: (value: string) => value.length >= 12 },
  { label: "One lowercase letter", test: (value: string) => /[a-z]/.test(value) },
  { label: "One uppercase letter", test: (value: string) => /[A-Z]/.test(value) },
  { label: "One number", test: (value: string) => /\d/.test(value) },
  { label: "One special character", test: (value: string) => /[^A-Za-z0-9\s]/.test(value) },
];

export default function RegisterPage() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [profileImage, setProfileImage] = useState<File | null>(null);

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    if (!firstName.trim() || !lastName.trim()) {
      setError("Enter your first and last name.");
      return;
    }
    if (!isStrongPassword(password)) {
      setError("Choose a password that meets all the requirements below.");
      return;
    }
    if (password !== confirmPassword) {
      setError("The passwords do not match.");
      return;
    }
    if (profileImage && profileImage.size > MAX_PROFILE_IMAGE_BYTES) {
      setError("Choose a profile photo that is 5 MB or smaller.");
      return;
    }
    setIsSubmitting(true);
    try {
      const tokens = await register({
        email,
        password,
        first_name: firstName,
        last_name: lastName,
        profile_image: profileImage,
      });
      saveTokens(tokens);
      navigate("/account", { replace: true });
    } catch (error) {
      setError(error instanceof Error ? error.message : "Registration failed.");
    } finally {
      setIsSubmitting(false);
    }
  }
  return (
    <AuthShell>
      <form className="auth-form" onSubmit={handleSubmit} aria-busy={isSubmitting}>
        <header className="auth-form-heading">
          <p className="auth-eyebrow">New customer</p>
          <h1>Open your account</h1>
          <p>Enter your details to get started with Demo Bank.</p>
        </header>

        <div className="auth-name-row">
          <div className="auth-field">
            <label htmlFor="firstName">First name</label>
            <input
              id="firstName"
              type="text"
              maxLength={100}
              value={firstName}
              onChange={(event) => setFirstName(event.target.value)}
              autoComplete="given-name"
              required
            />
          </div>

          <div className="auth-field">
            <label htmlFor="lastName">Last name</label>
            <input
              id="lastName"
              type="text"
              maxLength={100}
              value={lastName}
              onChange={(event) => setLastName(event.target.value)}
              autoComplete="family-name"
              required
            />
          </div>
        </div>

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
          <label htmlFor="profileImage">Profile photo (optional)</label>
          <input
            id="profileImage"
            type="file"
            accept="image/jpeg,image/png,image/webp"
            onChange={(event) => {
              setProfileImage(event.target.files?.[0] ?? null);
            }}
            aria-describedby="profile-image-hint"
          />
          <p className="auth-hint" id="profile-image-hint">
            JPEG, PNG, or WebP, up to 5 MB.
          </p>
        </div>

        <div className="auth-field">
          <label htmlFor="password">Create a password</label>
          <div className="auth-password-input-wrapper">
            <input
              id="password"
              type={showPassword ? "text" : "password"}
              minLength={12}
              maxLength={72}
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              autoComplete="new-password"
              aria-describedby="password-hint"
              required
            />
            <button
              type="button"
              className="auth-password-toggle"
              onClick={() => setShowPassword((previous) => !previous)}
              aria-label={showPassword ? "Hide password" : "Show password"}
            >
              {showPassword ? "Hide" : "Show"}
            </button>
          </div>
          <ul className="auth-password-checklist" id="password-hint" aria-live="polite">
            {passwordChecks.map((check) => {
              const isMet = check.test(password);

              return (
                <li
                  key={check.label}
                  className={isMet ? "password-check is-met" : "password-check"}
                >
                  <span className="password-check-indicator" aria-hidden="true">
                    ✓
                  </span>
                  <span>{check.label}</span>
                </li>
              );
            })}
          </ul>
        </div>

        <div className="auth-field">
          <label htmlFor="confirmPassword">Confirm password</label>
          <div className="auth-password-input-wrapper">
            <input
              id="confirmPassword"
              type={showConfirmPassword ? "text" : "password"}
              minLength={12}
              maxLength={72}
              value={confirmPassword}
              onChange={(event) => setConfirmPassword(event.target.value)}
              autoComplete="new-password"
              required
            />
            <button
              type="button"
              className="auth-password-toggle"
              onClick={() => setShowConfirmPassword((previous) => !previous)}
              aria-label={showConfirmPassword ? "Hide confirm password" : "Show confirm password"}
            >
              {showConfirmPassword ? "Hide" : "Show"}
            </button>
          </div>
        </div>

        {error && (
          <p className="error-message" role="alert">
            {error}
          </p>
        )}

        <button className="auth-primary-action" type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Creating account..." : "Create account"}
        </button>

        <p className="auth-form-footer">
          Already bank with us? <Link to="/login">Sign in</Link>
        </p>
      </form>
    </AuthShell>
  );
}
