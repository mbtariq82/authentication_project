import {
  apiRequest,
  clearTokens,
  getErrorMessage,
  isAuthenticated,
  login,
  parseResponse,
  refreshTokens,
} from "./api.js";

const loginForm = document.querySelector("#login-form");
const loginButton = document.querySelector("#login-button");

const meButton = document.querySelector("#me-button");
const adminButton = document.querySelector("#admin-button");
const refreshButton = document.querySelector("#refresh-button");
const logoutButton = document.querySelector("#logout-button");

const statusElement = document.querySelector("#status");
const outputElement = document.querySelector("#output");

loginForm.addEventListener("submit", handleLogin);
meButton.addEventListener("click", handleCurrentUser);
adminButton.addEventListener("click", handleAdminRequest);
refreshButton.addEventListener("click", handleManualRefresh);
logoutButton.addEventListener("click", handleLogout);

updateStatus();

async function handleLogin(event) {
  event.preventDefault();

  const username = document.querySelector("#username").value.trim();
  const password = document.querySelector("#password").value;

  setButtonLoading(loginButton, true, "Logging in...");

  try {
    const tokens = await login(username, password);

    showOutput({
      message: "Login successful",
      token_type: tokens.token_type,
      access_token_received: Boolean(tokens.access_token),
      refresh_token_received: Boolean(tokens.refresh_token),
    });

    updateStatus("Logged in");
  } catch (error) {
    showError(error);
    updateStatus("Login failed");
  } finally {
    setButtonLoading(loginButton, false, "Log in");
  }
}

async function handleCurrentUser() {
  await callProtectedEndpoint("/users/me");
}

async function handleAdminRequest() {
  /*
   * Change this path if your endpoint is under a router prefix,
   * for example "/users/admin-only".
   */
  await callProtectedEndpoint("/users/admin");
}

async function callProtectedEndpoint(path) {
  try {
    updateStatus(`Calling ${path}...`);

    const response = await apiRequest(path);
    const data = await parseResponse(response);

    if (!response.ok) {
      throw new Error(
        getErrorMessage(
          data,
          `Request failed with status ${response.status}.`,
        ),
      );
    }

    showOutput(data);
    updateStatus(`Request to ${path} succeeded`);
  } catch (error) {
    showError(error);
    updateStatus("Request failed");
  }
}

async function handleManualRefresh() {
  try {
    updateStatus("Refreshing tokens...");

    const tokens = await refreshTokens();

    showOutput({
      message: "Tokens refreshed",
      token_type: tokens.token_type,
      access_token_received: Boolean(tokens.access_token),
      refresh_token_received: Boolean(tokens.refresh_token),
    });

    updateStatus("Tokens refreshed successfully");
  } catch (error) {
    showError(error);
    updateStatus("Token refresh failed");
  }
}

function handleLogout() {
  clearTokens();

  loginForm.reset();
  showOutput({ message: "Local tokens cleared" });
  updateStatus("Not logged in");
}

function updateStatus(message) {
  if (message) {
    statusElement.textContent = message;
    return;
  }

  statusElement.textContent = isAuthenticated()
    ? "Logged in"
    : "Not logged in";
}

function showOutput(data) {
  outputElement.textContent = JSON.stringify(data, null, 2);
}

function showError(error) {
  outputElement.textContent = JSON.stringify(
    {
      error:
        error instanceof Error
          ? error.message
          : "An unknown error occurred.",
    },
    null,
    2,
  );
}

function setButtonLoading(button, isLoading, text) {
  button.disabled = isLoading;
  button.textContent = text;
}