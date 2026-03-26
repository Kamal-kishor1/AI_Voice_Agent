"""Seed script: Demo contacts, conversation, and sample tasks for local dev."""

from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from seeds.users import DEMO_USER_ID

# Fixed UUIDs for reproducible dev environments
CONV_ID = UUID("00000000-0000-4000-b000-000000000001")
MSG_1_ID = UUID("00000000-0000-4000-c000-000000000001")
MSG_2_ID = UUID("00000000-0000-4000-c000-000000000002")


async def seed_contacts(session: AsyncSession) -> None:
    """Insert sample contacts for the demo user."""

    result = await session.execute(
        text("SELECT COUNT(*) FROM contacts WHERE user_id = :uid"),
        {"uid": str(DEMO_USER_ID)},
    )
    if result.scalar_one() > 0:
        print("  ⏭  Contacts already seeded, skipping.")
        return

    contacts = [
        {
            "user_id": str(DEMO_USER_ID),
            "name": "Arjun Mehta",
            "email": "arjun.mehta@example.com",
            "phone": "+919876543210",
            "relationship": "colleague",
        },
        {
            "user_id": str(DEMO_USER_ID),
            "name": "Priya Sharma",
            "email": "priya.sharma@example.com",
            "phone": "+919876543211",
            "relationship": "client",
        },
        {
            "user_id": str(DEMO_USER_ID),
            "name": "Raj Patel",
            "email": "raj.patel@example.com",
            "phone": "+919876543212",
            "relationship": "colleague",
        },
        {
            "user_id": str(DEMO_USER_ID),
            "name": "Ananya Gupta",
            "email": "ananya.gupta@example.com",
            "phone": "+919876543213",
            "relationship": "friend",
        },
    ]

    for contact in contacts:
        await session.execute(
            text(
                """
                INSERT INTO contacts (user_id, name, email, phone, relationship)
                VALUES (:user_id, :name, :email, :phone, :relationship)
                """
            ),
            contact,
        )

    await session.commit()
    print("  ✅  Seeded 4 demo contacts.")


async def seed_conversation(session: AsyncSession) -> None:
    """Insert a sample conversation with two messages."""

    result = await session.execute(
        text("SELECT id FROM conversations WHERE id = :id"),
        {"id": str(CONV_ID)},
    )
    if result.scalar_one_or_none() is not None:
        print("  ⏭  Demo conversation already seeded, skipping.")
        return

    await session.execute(
        text(
            """
            INSERT INTO conversations (id, user_id, title, status)
            VALUES (:id, :user_id, :title, 'active')
            """
        ),
        {
            "id": str(CONV_ID),
            "user_id": str(DEMO_USER_ID),
            "title": "Welcome to Alex",
        },
    )

    await session.execute(
        text(
            """
            INSERT INTO messages (id, conversation_id, role, content, intent, confidence)
            VALUES (:id, :conv_id, 'user', :content, :intent, :confidence)
            """
        ),
        {
            "id": str(MSG_1_ID),
            "conv_id": str(CONV_ID),
            "content": "Hey Alex, what can you do?",
            "intent": "general_info",
            "confidence": 0.95,
        },
    )

    await session.execute(
        text(
            """
            INSERT INTO messages (id, conversation_id, role, content)
            VALUES (:id, :conv_id, 'assistant', :content)
            """
        ),
        {
            "id": str(MSG_2_ID),
            "conv_id": str(CONV_ID),
            "content": (
                "Hi Kamal! I'm Alex, your personal AI assistant. I can help you with: "
                "managing tasks and reminders, searching your files, sending emails and "
                "WhatsApp messages, scheduling meetings, transcribing calls, and generating "
                "your daily morning briefing. Just tell me what you need!"
            ),
        },
    )

    await session.commit()
    print("  ✅  Seeded demo conversation with 2 messages.")


async def seed_tasks(session: AsyncSession) -> None:
    """Insert sample tasks for the demo user."""

    result = await session.execute(
        text("SELECT COUNT(*) FROM tasks WHERE user_id = :uid"),
        {"uid": str(DEMO_USER_ID)},
    )
    if result.scalar_one() > 0:
        print("  ⏭  Tasks already seeded, skipping.")
        return

    tasks = [
        {
            "user_id": str(DEMO_USER_ID),
            "title": "Review Q3 sales report",
            "description": "Check the quarterly figures before the board meeting",
            "priority": "high",
            "status": "todo",
            "source": "manual",
        },
        {
            "user_id": str(DEMO_USER_ID),
            "title": "Call Arjun about project timeline",
            "description": "Discuss the Phase 2 delivery schedule",
            "priority": "medium",
            "status": "in_progress",
            "source": "voice",
        },
        {
            "user_id": str(DEMO_USER_ID),
            "title": "Prepare slides for Monday standup",
            "description": None,
            "priority": "low",
            "status": "todo",
            "source": "meeting_extract",
        },
    ]

    for task in tasks:
        await session.execute(
            text(
                """
                INSERT INTO tasks (user_id, title, description, priority, status, source)
                VALUES (:user_id, :title, :description, :priority, :status, :source)
                """
            ),
            task,
        )

    await session.commit()
    print("  ✅  Seeded 3 demo tasks.")
