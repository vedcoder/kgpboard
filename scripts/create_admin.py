"""Create an admin user (admins can't be created through the public API).

Usage:
    PYTHONPATH=. uv run python scripts/create_admin.py <name> <email> <password>
"""

import asyncio
import sys

from app.core.exceptions import EmailAlreadyExistsError
from app.db.session import AsyncSessionLocal, engine
from app.models.user import UserRole
from app.services import user as user_service


async def main() -> None:
    if len(sys.argv) != 4:
        print("usage: create_admin.py <name> <email> <password>")
        raise SystemExit(1)

    name, email, password = sys.argv[1:4]
    async with AsyncSessionLocal() as session:
        try:
            user = await user_service.create_user(
                session,
                name=name,
                email=email,
                password=password,
                role=UserRole.admin,
            )
        except EmailAlreadyExistsError as exc:
            print(f"Error: {exc.message}")
            raise SystemExit(1) from None
        print(f"Created admin '{user.name}' <{user.email}> id={user.id}")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
