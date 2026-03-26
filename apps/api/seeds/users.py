"""Seed script: Default admin user and demo user."""

from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# Fixed UUIDs for reproducible dev environments
ADMIN_USER_ID = UUID("00000000-0000-4000-a000-000000000001")
DEMO_USER_ID = UUID("00000000-0000-4000-a000-000000000002")


async def seed_users(session: AsyncSession) -> None:
    """Insert default admin and demo users if they don't already exist."""

    # Check if admin already exists
    result = await session.execute(
        text("SELECT id FROM users WHERE id = :id"),
        {"id": str(ADMIN_USER_ID)},
    )
    if result.scalar_one_or_none() is not None:
        print("  ⏭  Users already seeded, skipping.")
        return

    # Admin user — password is "admin123" bcrypt-hashed
    # $2b$12$LJ3m4ys4Dz2eFqKxGqK0/.J5aE1DBySX.VUgJnRQoqXjCLk0G1FBi
    await session.execute(
        text(
            """
            INSERT INTO users (id, email, password_hash, full_name, role, is_active)
            VALUES (:id, :email, :password_hash, :full_name, :role, TRUE)
            """
        ),
        {
            "id": str(ADMIN_USER_ID),
            "email": "admin@antigravity.dev",
            "password_hash": "$2b$12$LJ3m4ys4Dz2eFqKxGqK0/.J5aE1DBySX.VUgJnRQoqXjCLk0G1FBi",
            "full_name": "Alex Admin",
            "role": "admin",
        },
    )

    # Demo user — password is "demo123"
    # $2b$12$Wc7kT6bJZ3Q5vN1yFz8x5ug8sS0N2p3L6F9TqAz1gY4bK7mR5dV.e
    await session.execute(
        text(
            """
            INSERT INTO users (id, email, password_hash, full_name, role, is_active)
            VALUES (:id, :email, :password_hash, :full_name, :role, TRUE)
            """
        ),
        {
            "id": str(DEMO_USER_ID),
            "email": "kamal@antigravity.dev",
            "password_hash": "$2b$12$Wc7kT6bJZ3Q5vN1yFz8x5ug8sS0N2p3L6F9TqAz1gY4bK7mR5dV.e",
            "full_name": "Kamal Kishor",
            "role": "user",
        },
    )

    await session.commit()
    print("  ✅  Seeded admin and demo users.")
