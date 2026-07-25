import { useEffect, useState } from "react";
import { useNavigate } from "react-router";

import { logout } from "../api/authClient";
import {
  getUserProfile,
  type UserResponse,
} from "../api/userClient";
import { clearTokens } from "../auth/tokenStorage";

export default function ProfilePage() {
  const navigate = useNavigate();
  const [user, setUser] = useState<UserResponse | null>(null);
  const [isLoggingOut, setIsLoggingOut] = useState(false);  // for disabling logout button
  
  useEffect(() => { //
    async function loadCurrentUser() {
      try {
        const currentUser = await getUserProfile();
        setUser(currentUser);
      } catch {
        clearTokens();
        navigate("/login", { replace: true });
      }
    }
    void loadCurrentUser();
  }, [navigate]);

  async function handleLogout() {
    setIsLoggingOut(true);
    try {
      await logout();
    } catch (error) {
      console.error("Backend logout failed", error);
    } finally {
      clearTokens();
      navigate("/login", { replace: true });
    }
  }
  
  if (!user) {
    return null;
  }

  return (
    <main className="profile-page">
      <div className="user-details-card">
        <header className="user-details-header">
          <p>USER PROFILE</p>
        </header>
        <dl className="user-details">
          <div>
            <dt>User ID</dt>
            <dd>{user.id}</dd>
          </div>
          <div>
            <dt>Email</dt>
            <dd>{user.email}</dd>
          </div>
        </dl>

        <button
          className="logout-button"
          type="button"
          onClick={handleLogout}
          disabled={isLoggingOut}
        >
          {isLoggingOut ? "Logging out..." : "Log out"}
        </button>
      </div>
    </main>
  );
}