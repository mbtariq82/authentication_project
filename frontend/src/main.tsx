import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router";
import { GoogleOAuthProvider } from "@react-oauth/google";
import App from "./App";
import "./index.css";

const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;

const application = (
  <BrowserRouter>
    <App />
  </BrowserRouter>
);

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    {googleClientId ? (
      <GoogleOAuthProvider clientId={googleClientId}>
        {application}
      </GoogleOAuthProvider>
    ) : (
      application
    )}
  </StrictMode>,
);
