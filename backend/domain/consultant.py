from dataclasses import dataclass
from datetime import datetime

from enums import Batch, PlacementStatus


@dataclass(slots=True)
class Consultant:
    user_id: int
    email: str
    first_name: str
    last_name: str
    created_at: datetime
    id: int | None = None
    batch: Batch | None = None
    placement_status: PlacementStatus = PlacementStatus.ONBOARDING
    client: str | None = None
