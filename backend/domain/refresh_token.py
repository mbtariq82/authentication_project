from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True, slots=True)
class RefreshToken:
    token: str
    user_id: int
    expires_at: datetime

    def is_expired(self, now: datetime | None = None) -> bool:
        now = now or datetime.now(timezone.utc)
        return self.expires_at <= now
