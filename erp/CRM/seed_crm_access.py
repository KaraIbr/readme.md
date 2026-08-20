"""Seed CRM access and roles for existing IAM users."""

import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

DB_URL = "sqlite+aiosqlite:///./ventura.db"

ROLE_MAP = {
    "admin@verp.com": "ADMIN",
    "manager@verp.com": "MANAGER",
    "sales@verp.com": "SALES",
    "tech@verp.com": "TECH",
}


async def main() -> None:
    engine = create_async_engine(DB_URL)
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT id, email FROM iam_user"))
        users = result.all()
        print(f"Found {len(users)} IAM users")

        for user_id, email in users:
            role = ROLE_MAP.get(email)
            if role is None:
                print(f"  Skip {email}: no role mapping")
                continue

            existing_iam = await conn.execute(
                text(
                    "SELECT id FROM iam_service_access WHERE user_id = :uid AND service_key = 'crm'"
                ),
                {"uid": user_id},
            )
            if not existing_iam.first():
                await conn.execute(
                    text(
                        "INSERT INTO iam_service_access "
                        "(user_id, service_key, is_active, granted_by) "
                        "VALUES (:uid, 'crm', 1, :uid)"
                    ),
                    {"uid": user_id},
                )
                print(f"  + IAMServiceAccess for {email}")

            existing_crm = await conn.execute(
                text("SELECT user_id FROM crm_user_access WHERE user_id = :uid"),
                {"uid": user_id},
            )
            if not existing_crm.first():
                await conn.execute(
                    text(
                        "INSERT INTO crm_user_access "
                        "(user_id, role, is_active, changed_by) "
                        "VALUES (:uid, :role, 1, :uid)"
                    ),
                    {"uid": user_id, "role": role},
                )
                print(f"  + CRMUserAccess ({role}) for {email}")
            else:
                print(f"  Already has CRM access ({role}) for {email}")

        await conn.commit()
        print("\nDone. Restart CRM backend for JWT secret to take effect.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
