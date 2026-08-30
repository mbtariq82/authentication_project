import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class ApprovalStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXECUTED = "EXECUTED"
    FAILED = "FAILED"


class ApprovalService:
    """
    Tracks admin actions (emails, Instagram posts, ...) that require
    human approval before they're actually sent/published.

    NOTE: this is an in-memory store. That's fine for a single dev
    process, but it will not survive a restart and will not work
    correctly if the API runs with multiple workers, since each
    worker would have its own store. For production, back this with
    a real table (id, action_type, payload JSON, status, created_by,
    created_at, decided_at) instead of the dict below — the public
    method signatures here are written so that swap wouldn't change
    any calling code.
    """

    def __init__(self):
        self._approvals: dict[str, dict[str, Any]] = {}

    def create(
        self,
        action_type: str,
        payload: dict[str, Any],
        created_by: Optional[str] = None,
    ) -> dict[str, Any]:

        approval_id = str(uuid.uuid4())

        approval = {
            "id": approval_id,
            "action_type": action_type,
            "payload": payload,
            "status": ApprovalStatus.PENDING,
            "created_by": created_by,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "decided_at": None,
            "result": None,
        }

        self._approvals[approval_id] = approval

        logger.info(
            "APPROVAL_SERVICE | create | id=%s | action_type=%s | created_by=%s",
            approval_id, action_type, created_by,
        )

        return approval

    def get(self, approval_id: str) -> Optional[dict[str, Any]]:
        return self._approvals.get(approval_id)

    def list_pending(self) -> list[dict[str, Any]]:
        return [
            a for a in self._approvals.values()
            if a["status"] == ApprovalStatus.PENDING
        ]

    def mark_approved(self, approval_id: str) -> dict[str, Any]:
        approval = self._require_pending(approval_id)

        approval["status"] = ApprovalStatus.APPROVED
        approval["decided_at"] = datetime.now(timezone.utc).isoformat()

        logger.info("APPROVAL_SERVICE | approved | id=%s", approval_id)

        return approval

    def reject(self, approval_id: str) -> dict[str, Any]:
        approval = self._require_pending(approval_id)

        approval["status"] = ApprovalStatus.REJECTED
        approval["decided_at"] = datetime.now(timezone.utc).isoformat()

        logger.info("APPROVAL_SERVICE | rejected | id=%s", approval_id)

        return approval

    def mark_executed(self, approval_id: str, result: Any) -> dict[str, Any]:
        approval = self._approvals[approval_id]
        approval["status"] = ApprovalStatus.EXECUTED
        approval["result"] = result

        logger.info(
            "APPROVAL_SERVICE | executed | id=%s | result=%s",
            approval_id, result,
        )

        return approval

    def mark_failed(self, approval_id: str, error: str) -> dict[str, Any]:
        approval = self._approvals[approval_id]
        approval["status"] = ApprovalStatus.FAILED
        approval["result"] = {"error": error}

        logger.warning(
            "APPROVAL_SERVICE | failed | id=%s | error=%s",
            approval_id, error,
        )

        return approval

    def update_payload(self, approval_id: str, **updates: Any) -> dict[str, Any]:
        """Lets the API layer patch a payload before execution, e.g.
        attaching an image_url an admin supplies at approval time."""
        approval = self._approvals[approval_id]
        approval["payload"].update(updates)

        logger.info(
            "APPROVAL_SERVICE | payload updated | id=%s | keys=%s",
            approval_id, list(updates.keys()),
        )

        return approval

    def _require_pending(self, approval_id: str) -> dict[str, Any]:
        approval = self._approvals.get(approval_id)

        if not approval:
            logger.warning("APPROVAL_SERVICE | not found | id=%s", approval_id)
            raise KeyError(f"No approval found for id {approval_id}")

        if approval["status"] != ApprovalStatus.PENDING:
            logger.warning(
                "APPROVAL_SERVICE | not pending | id=%s | status=%s",
                approval_id, approval["status"],
            )
            raise ValueError(
                f"Approval {approval_id} is not pending "
                f"(status={approval['status']})"
            )

        return approval


# Module-level singleton so the agent (which creates approvals) and the
# API routes (which approve/reject/execute them) share the same queue.
approval_service = ApprovalService()