"""
Seed runner for Alex development environment.

Usage:
    cd apps/api
    python -m seeds.run

Prerequisites:
    - PostgreSQL must be running (via docker-compose or local install)
    - Alembic migrations must be applied first (`alembic upgrade head`)
"""

import asyncio
import sys

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from seeds.users import seed_users
from seeds.demo_data import seed_contacts, seed_conversation, seed_tasks


async def main() -> None:
    settings = get_settings()
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    print("🌱 Alex Seed Runner")
    print("=" * 50)

    async with session_factory() as session:
        try:
            print("\n📦 Step 1/4: Seeding users...")
            await seed_users(session)

            print("\n📇 Step 2/4: Seeding contacts...")
            await seed_contacts(session)

            print("\n💬 Step 3/4: Seeding demo conversation...")
            await seed_conversation(session)

            print("\n📋 Step 4/4: Seeding demo tasks...")
            await seed_tasks(session)

            print("\n" + "=" * 50)
            print("✅ All seeds completed successfully!")

        except Exception as e:
            print(f"\n❌ Seed failed: {e}")
            sys.exit(1)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
