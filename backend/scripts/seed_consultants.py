import asyncio
import csv
from datetime import datetime
from pathlib import Path

from sqlalchemy import select

from database import async_session_factory
from enums import PlacementStatus, Role
from models import ConsultantRow, UserRow


CSV_PATH = (
    Path(__file__).resolve().parents[1]
    / "seed_data"
    / "consultants-seed.csv"
)


async def seed_consultants() -> None:
    async with async_session_factory() as session:
        existing_emails = set(
            (
                await session.scalars(
                    select(UserRow.email)
                )
            ).all()
        )

        with CSV_PATH.open(newline="", encoding="utf-8") as file:
            rows = csv.DictReader(file)

            for row in rows:
                if row["email"] in existing_emails:
                    continue

                user = UserRow(
                    email=row["email"],
                    first_name=row["first_name"],
                    last_name=row["last_name"],
                    role=Role(row["role"]),
                    hashed_password=None,
                )

                user.consultant = ConsultantRow(
                    batch=row["batch"],
                    placement_status=PlacementStatus(
                        row["placement_status"]
                    ),
                    client=row["client"] or None,
                    created_at=datetime.fromisoformat(
                        row["created_at"].replace("Z", "+00:00")
                    ),
                )

                session.add(user)
                existing_emails.add(row["email"])

        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed_consultants())
