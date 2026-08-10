from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal

from enums import AccountStatus, ApprovalStatus


@dataclass(slots=True)
class AccountType:
    name: str
    interest_rate: Decimal = Decimal("0.00")
    minimum_balance: Decimal = Decimal("0.00")
    allows_overdraft: bool = False
    is_active: bool = True
    id: int | None = None

@dataclass(slots=True)
class Balance:
    account_id: int
    ledger_balance: Decimal = Decimal("0.00")
    available_balance: Decimal = Decimal("0.00")
    id: int | None = None
    updated_at: datetime | None = None

@dataclass(slots=True)
class Account:
    user_id: int
    account_type_id: int
    id: int | None = None
    account_number: str | None = None
    admin_approved: ApprovalStatus = ApprovalStatus.PENDING
    status: AccountStatus = AccountStatus.ACTIVE
    approved_by: int | None = None
    approved_at: datetime | None = None
    rejection_reason: str | None = None
    created_at: datetime | None = None
    closed_at: datetime | None = None

    @classmethod
    def apply_for(cls, user_id: int, account_type_id: int) -> "Account":
        return cls(user_id=user_id, account_type_id=account_type_id)

    def approve(
        self,
        admin_id: int,
        account_number: str,
        now: datetime | None = None,
    ) -> None:
        if self.admin_approved is not ApprovalStatus.PENDING:
            raise ValueError("Only a pending account can be approved")
        self.admin_approved = ApprovalStatus.APPROVED
        self.account_number = account_number
        self.approved_by = admin_id
        self.approved_at = now or datetime.now(timezone.utc)

    def reject(
        self,
        admin_id: int,
        reason: str,
        now: datetime | None = None,
    ) -> None:
        if self.admin_approved is not ApprovalStatus.PENDING:
            raise ValueError("Only a pending account can be rejected.")
        self.admin_approved = ApprovalStatus.REJECTED
        self.rejection_reason = reason
        self.approved_by = admin_id
        self.approved_at = now or datetime.now(timezone.utc)

    def freeze(self) -> None:
        if self.status is not AccountStatus.ACTIVE:
            raise ValueError("Only an active account can be frozen.")
        self.status = AccountStatus.FROZEN

    def unfreeze(self) -> None:
        if self.status is not AccountStatus.FROZEN:
            raise ValueError("Only a frozen account can be unfrozen.")
        self.status = AccountStatus.ACTIVE

    def close(self, now: datetime | None = None) -> None:
        if self.status is AccountStatus.CLOSED:
            raise ValueError("This account is already closed.")
        self.status = AccountStatus.CLOSED
        self.closed_at = now or datetime.now(timezone.utc)

    def is_transactable(self) -> bool:
        return (
            self.admin_approved is ApprovalStatus.APPROVED
            and self.status is AccountStatus.ACTIVE
        )