import { Navigate, Route, Routes } from "react-router";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import LoginPage from "./pages/LoginPage";
import CustomerHomePage from "./pages/CustomerHomePage";
import DashboardPage from "./pages/DashboardPage";
import RegisterPage from "./pages/RegisterPage";
import ConsultantsPage from "./pages/Consultants";
import AddConsultantPage from "./pages/AddConsultantPage";
import BeneficiariesPage from "./pages/BeneficiariesPage";
import TransactionsPage from "./pages/TransactionsPage";
import TransactionHistoryPage from "./pages/TransactionHistoryPage";
import { routes } from "./routes";
import AdminDashboard from "./components/Admin/AdminDashboard";
import "./App.css";

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Routes>
        <Route path={routes.login} element={<LoginPage />} />
        <Route path={routes.account} element={<CustomerHomePage />} />
        <Route path={routes.beneficiaries} element={<BeneficiariesPage />} />
        <Route path={routes.transactions} element={<TransactionsPage />} />
        <Route
          path={routes.transactionHistory}
          element={<TransactionHistoryPage />}
        />
        <Route path="/profile" element={<Navigate to="/account" replace />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/admin/dashboard" element={<DashboardPage />} />
        <Route path="/admin/consultants" element={<ConsultantsPage />} />
        <Route path="/admin/consultants/new" element={<AddConsultantPage />} />
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="/bank/admin/dashboard" element={<AdminDashboard />} />
      </Routes>
    </QueryClientProvider>
  );
}

export default App;
