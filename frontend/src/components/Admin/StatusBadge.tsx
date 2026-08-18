import type {
  AccountStatus,
  CardStatus,
  LoanStatus,
} from "../../types/admin";

interface StatusBadgeProps {
  status: AccountStatus | LoanStatus | CardStatus;
}

export default function StatusBadge({ status }: StatusBadgeProps) {
  return <span className={`badge ${status}`}>{status}</span>;
}
