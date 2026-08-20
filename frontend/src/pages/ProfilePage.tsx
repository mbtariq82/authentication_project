import {
  useEffect,
  useMemo,
  useRef,
  useState,
  type FormEvent,
} from "react";
import { useNavigate } from "react-router";

import {
  getUserProfile,
  updateProfileImage,
  type UserResponse,
} from "../api/userClient";
import { clearTokens } from "../auth/tokenStorage";
import CustomerNavigation from "../components/CustomerNavigation";
import { routes } from "../routes";

const MAX_PROFILE_IMAGE_BYTES = 5 * 1024 * 1024;
const ACCEPTED_PROFILE_IMAGE_TYPES = new Set([
  "image/jpeg",
  "image/png",
  "image/webp",
]);

export default function ProfilePage() {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [user, setUser] = useState<UserResponse | null>(null);
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [profileImageFailed, setProfileImageFailed] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const previewUrl = useMemo(
    () => (selectedImage ? URL.createObjectURL(selectedImage) : null),
    [selectedImage],
  );

  useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl);
    };
  }, [previewUrl]);

  useEffect(() => {
    async function loadCurrentUser() {
      try {
        setUser(await getUserProfile());
      } catch {
        clearTokens();
        navigate(routes.login, { replace: true });
      }
    }

    void loadCurrentUser();
  }, [navigate]);

  function handleImageSelection(file: File | null) {
    setError("");
    setMessage("");

    if (!file) {
      setSelectedImage(null);
      return;
    }
    if (!ACCEPTED_PROFILE_IMAGE_TYPES.has(file.type)) {
      setSelectedImage(null);
      setError("Choose a JPEG, PNG, or WebP image.");
      if (fileInputRef.current) fileInputRef.current.value = "";
      return;
    }
    if (file.size > MAX_PROFILE_IMAGE_BYTES) {
      setSelectedImage(null);
      setError("Choose a profile photo that is 5 MB or smaller.");
      if (fileInputRef.current) fileInputRef.current.value = "";
      return;
    }

    setSelectedImage(file);
    setProfileImageFailed(false);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedImage) return;

    setError("");
    setMessage("");
    setIsSubmitting(true);

    try {
      const updatedUser = await updateProfileImage(selectedImage);
      setUser(updatedUser);
      setSelectedImage(null);
      setProfileImageFailed(false);
      setMessage("Your profile photo has been updated.");
      if (fileInputRef.current) fileInputRef.current.value = "";
    } catch (uploadError) {
      setError(
        uploadError instanceof Error
          ? uploadError.message
          : "Failed to update profile photo.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  if (!user) {
    return (
      <main className="customer-home customer-home-loading">
        <p role="status">Loading your profile…</p>
      </main>
    );
  }

  const fullName = [user.first_name, user.last_name].filter(Boolean).join(" ");
  const initials =
    [user.first_name, user.last_name]
      .filter(Boolean)
      .map((name) => name[0])
      .join("")
      .toUpperCase() || user.email[0].toUpperCase();
  const imageUrl = previewUrl ?? user.profile_image_url;
  const showProfileImage = imageUrl && !profileImageFailed;
  const address = [user.address, user.city, user.postcode, user.country]
    .filter(Boolean)
    .join(", ");

  return (
    <main className="customer-home">
      <CustomerNavigation user={user} />

      <section className="customer-content profile-page">
        <header className="profile-page-heading">
          <p className="auth-eyebrow">Your account</p>
          <h1>Customer profile</h1>
          <p>Review your personal details and keep your profile photo current.</p>
        </header>

        <div className="profile-layout">
          <section className="profile-photo-card" aria-labelledby="photo-title">
            <div className="profile-photo-preview">
              {showProfileImage ? (
                <img
                  src={imageUrl}
                  alt={`${fullName || "Customer"}'s profile`}
                  onError={() => setProfileImageFailed(true)}
                />
              ) : (
                <span aria-hidden="true">{initials}</span>
              )}
            </div>

            <div>
              <p className="customer-card-label">Profile photo</p>
              <h2 id="photo-title">Choose a new photo</h2>
              <p className="profile-photo-help">
                Use a JPEG, PNG, or WebP image up to 5 MB.
              </p>
            </div>

            <form className="profile-photo-form" onSubmit={handleSubmit}>
              <label className="profile-file-control" htmlFor="profile-image">
                <span>{selectedImage ? selectedImage.name : "Select photo"}</span>
                <input
                  ref={fileInputRef}
                  id="profile-image"
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  onChange={(event) =>
                    handleImageSelection(event.target.files?.[0] ?? null)
                  }
                />
              </label>

              <button
                className="profile-upload-button"
                type="submit"
                disabled={!selectedImage || isSubmitting}
              >
                {isSubmitting ? "Uploading…" : "Upload new photo"}
              </button>
            </form>

            {error && (
              <p className="profile-message profile-message-error" role="alert">
                {error}
              </p>
            )}
            {message && (
              <p className="profile-message profile-message-success" role="status">
                {message}
              </p>
            )}
          </section>

          <article className="customer-details-card profile-details-card">
            <header>
              <p className="customer-card-label">Your details</p>
              <h2>Personal information</h2>
            </header>
            <dl>
              <div>
                <dt>Name</dt>
                <dd>{fullName || "Not provided"}</dd>
              </div>
              <div>
                <dt>Email</dt>
                <dd>{user.email}</dd>
              </div>
              <div>
                <dt>Phone</dt>
                <dd>{user.phone || "Not provided"}</dd>
              </div>
              <div>
                <dt>Address</dt>
                <dd>{address || "Not provided"}</dd>
              </div>
              <div>
                <dt>Date of birth</dt>
                <dd>{user.dob || "Not provided"}</dd>
              </div>
            </dl>
          </article>
        </div>
      </section>
    </main>
  );
}
