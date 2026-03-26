"""phase 1 foundation

Revision ID: 202603260200
Revises:
Create Date: 2026-03-26 02:00:00
"""

from collections.abc import Iterable

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql


revision = "202603260200"
down_revision = None
branch_labels = None
depends_on = None


USER_SCOPED_TABLES = (
    "conversations",
    "action_logs",
    "contacts",
    "calendar_events",
    "tasks",
    "reminders",
    "files",
    "user_preferences",
    "meeting_summaries",
)


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("CREATE SCHEMA IF NOT EXISTS auth")
    op.execute(
        """
        CREATE OR REPLACE FUNCTION auth.uid()
        RETURNS uuid
        LANGUAGE sql
        STABLE
        AS $$
            SELECT COALESCE(
                NULLIF(current_setting('request.jwt.claim.sub', true), ''),
                '00000000-0000-0000-0000-000000000000'
            )::uuid;
        $$;
        """
    )
    op.execute(
        """
        CREATE OR REPLACE FUNCTION public.set_updated_at()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$;
        """
    )
    op.create_table(
        "users",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=150), nullable=False),
        sa.Column("avatar_url", sa.Text(), nullable=True),
        sa.Column("role", sa.String(length=20), nullable=False, server_default=sa.text("'user'")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("TRUE")),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("role IN ('admin','user')", name="ck_users_role_valid"),
        sa.UniqueConstraint("email", name="idx_users_email"),
    )

    op.create_table(
        "conversations",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True, server_default=sa.text("'New Conversation'")),
        sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'active'")),
        sa.Column("context_summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.CheckConstraint("status IN ('active','archived','deleted')", name="ck_conversations_status_valid"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE", onupdate="CASCADE"),
    )

    op.create_table(
        "messages",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("audio_url", sa.Text(), nullable=True),
        sa.Column("token_count", sa.Integer(), nullable=True),
        sa.Column("intent", sa.String(length=100), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.CheckConstraint("role IN ('user','assistant','system')", name="ck_messages_role_valid"),
        sa.CheckConstraint(
            "confidence IS NULL OR (confidence >= 0.0 AND confidence <= 1.0)",
            name="ck_messages_confidence_valid",
        ),
        sa.ForeignKeyConstraint(["conversation_id"], ["conversations.id"], ondelete="CASCADE", onupdate="CASCADE"),
    )

    op.create_table(
        "action_logs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("message_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("action_type", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'pending'")),
        sa.Column("input_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default=sa.text("'{}'::jsonb")),
        sa.Column("output_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default=sa.text("'{}'::jsonb")),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("status IN ('pending','running','success','failed')", name="ck_action_logs_status_valid"),
        sa.ForeignKeyConstraint(["message_id"], ["messages.id"], ondelete="CASCADE", onupdate="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE", onupdate="CASCADE"),
    )

    op.create_table(
        "contacts",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("relationship", sa.String(length=50), nullable=True),
        sa.Column("is_favorite", sa.Boolean(), nullable=False, server_default=sa.text("FALSE")),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE", onupdate="CASCADE"),
    )

    op.create_table(
        "calendar_events",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("attendees", postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default=sa.text("'[]'::jsonb")),
        sa.Column("recurrence_rule", sa.String(length=255), nullable=True),
        sa.Column("external_id", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'confirmed'")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.CheckConstraint("status IN ('confirmed','tentative','cancelled')", name="ck_calendar_events_status_valid"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE", onupdate="CASCADE"),
        sa.UniqueConstraint("external_id", name="idx_cal_external"),
    )

    op.create_table(
        "tasks",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("priority", sa.String(length=10), nullable=False, server_default=sa.text("'medium'")),
        sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'todo'")),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source", sa.String(length=50), nullable=False, server_default=sa.text("'manual'")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.CheckConstraint("priority IN ('low','medium','high','urgent')", name="ck_tasks_priority_valid"),
        sa.CheckConstraint("status IN ('todo','in_progress','done','cancelled')", name="ck_tasks_status_valid"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE", onupdate="CASCADE"),
    )
    op.create_table(
        "reminders",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("task_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("remind_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_recurring", sa.Boolean(), nullable=False, server_default=sa.text("FALSE")),
        sa.Column("recurrence_rule", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'pending'")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.CheckConstraint("status IN ('pending','sent','dismissed')", name="ck_reminders_status_valid"),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"], ondelete="SET NULL", onupdate="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE", onupdate="CASCADE"),
    )

    op.create_table(
        "files",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("mime_type", sa.String(length=100), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("storage_path", sa.Text(), nullable=False),
        sa.Column("is_indexed", sa.Boolean(), nullable=False, server_default=sa.text("FALSE")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE", onupdate="CASCADE"),
        sa.UniqueConstraint("storage_path", name="uq_files_storage_path"),
    )

    op.create_table(
        "file_embeddings",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("file_id", postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column("chunk_index", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("content_text", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(dim=1536), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["file_id"], ["files.id"], ondelete="CASCADE", onupdate="CASCADE"),
    )

    op.create_table(
        "user_preferences",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("key", sa.String(length=100), nullable=False),
        sa.Column("value", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("source", sa.String(length=50), nullable=False, server_default=sa.text("'learned'")),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.CheckConstraint(
            "confidence IS NULL OR (confidence >= 0.0 AND confidence <= 1.0)",
            name="ck_user_preferences_confidence_valid",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE", onupdate="CASCADE"),
    )

    op.create_table(
        "meeting_summaries",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("calendar_event_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("transcript_url", sa.Text(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("action_items", postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default=sa.text("'[]'::jsonb")),
        sa.Column("duration_minutes", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["calendar_event_id"], ["calendar_events.id"], ondelete="SET NULL", onupdate="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE", onupdate="CASCADE"),
    )

    op.create_index("idx_conv_user_id", "conversations", ["user_id"], unique=False)
    op.create_index("idx_conv_updated", "conversations", ["updated_at"], unique=False)
    op.create_index("idx_msg_conv_id_created", "messages", ["conversation_id", "created_at"], unique=False)
    op.create_index("idx_msg_intent", "messages", ["intent"], unique=False)
    op.create_index("idx_action_user_status", "action_logs", ["user_id", "status"], unique=False)
    op.create_index("idx_cal_user_time", "calendar_events", ["user_id", "start_time"], unique=False)
    op.create_index("idx_task_user_status", "tasks", ["user_id", "status"], unique=False)
    op.create_index("idx_task_due", "tasks", ["due_date"], unique=False)
    op.create_index("idx_remind_at", "reminders", ["remind_at"], unique=False)
    op.create_index("idx_file_user", "files", ["user_id"], unique=False)
    op.create_index("idx_pref_user_key", "user_preferences", ["user_id", "key"], unique=True)
    op.execute(
        """
        CREATE INDEX idx_embed_vector
        ON file_embeddings
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100)
        """
    )

    _attach_updated_at_triggers(
        (
            "users",
            "conversations",
            "contacts",
            "calendar_events",
            "tasks",
            "user_preferences",
        )
    )
    _enable_rls()


def downgrade() -> None:
    _drop_rls()
    _drop_updated_at_triggers(
        (
            "users",
            "conversations",
            "contacts",
            "calendar_events",
            "tasks",
            "user_preferences",
        )
    )

    op.execute("DROP INDEX IF EXISTS idx_embed_vector")
    op.drop_index("idx_pref_user_key", table_name="user_preferences")
    op.drop_index("idx_file_user", table_name="files")
    op.drop_index("idx_remind_at", table_name="reminders")
    op.drop_index("idx_task_due", table_name="tasks")
    op.drop_index("idx_task_user_status", table_name="tasks")
    op.drop_index("idx_cal_user_time", table_name="calendar_events")
    op.drop_index("idx_action_user_status", table_name="action_logs")
    op.drop_index("idx_msg_intent", table_name="messages")
    op.drop_index("idx_msg_conv_id_created", table_name="messages")
    op.drop_index("idx_conv_updated", table_name="conversations")
    op.drop_index("idx_conv_user_id", table_name="conversations")

    op.drop_table("meeting_summaries")
    op.drop_table("user_preferences")
    op.drop_table("file_embeddings")
    op.drop_table("files")
    op.drop_table("reminders")
    op.drop_table("tasks")
    op.drop_table("calendar_events")
    op.drop_table("contacts")
    op.drop_table("action_logs")
    op.drop_table("messages")
    op.drop_table("conversations")
    op.drop_table("users")

    op.execute("DROP FUNCTION IF EXISTS public.set_updated_at()")
    op.execute("DROP FUNCTION IF EXISTS auth.uid()")
    op.execute("DROP SCHEMA IF EXISTS auth")


def _attach_updated_at_triggers(tables: Iterable[str]) -> None:
    for table_name in tables:
        op.execute(
            f"""
            CREATE TRIGGER set_{table_name}_updated_at
            BEFORE UPDATE ON {table_name}
            FOR EACH ROW
            EXECUTE FUNCTION public.set_updated_at()
            """
        )


def _drop_updated_at_triggers(tables: Iterable[str]) -> None:
    for table_name in tables:
        op.execute(f"DROP TRIGGER IF EXISTS set_{table_name}_updated_at ON {table_name}")


def _enable_rls() -> None:
    op.execute("ALTER TABLE users ENABLE ROW LEVEL SECURITY")
    op.execute(
        """
        CREATE POLICY users_isolation ON users
        FOR ALL
        USING (id = auth.uid())
        WITH CHECK (id = auth.uid())
        """
    )

    for table_name in USER_SCOPED_TABLES:
        op.execute(f"ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY")
        op.execute(
            f"""
            CREATE POLICY {table_name}_isolation ON {table_name}
            FOR ALL
            USING (user_id = auth.uid())
            WITH CHECK (user_id = auth.uid())
            """
        )

    op.execute("ALTER TABLE messages ENABLE ROW LEVEL SECURITY")
    op.execute(
        """
        CREATE POLICY messages_isolation ON messages
        FOR ALL
        USING (
            EXISTS (
                SELECT 1
                FROM conversations
                WHERE conversations.id = messages.conversation_id
                  AND conversations.user_id = auth.uid()
            )
        )
        WITH CHECK (
            EXISTS (
                SELECT 1
                FROM conversations
                WHERE conversations.id = messages.conversation_id
                  AND conversations.user_id = auth.uid()
            )
        )
        """
    )

    op.execute("ALTER TABLE file_embeddings ENABLE ROW LEVEL SECURITY")
    op.execute(
        """
        CREATE POLICY file_embeddings_isolation ON file_embeddings
        FOR ALL
        USING (
            EXISTS (
                SELECT 1
                FROM files
                WHERE files.id = file_embeddings.file_id
                  AND files.user_id = auth.uid()
            )
        )
        WITH CHECK (
            EXISTS (
                SELECT 1
                FROM files
                WHERE files.id = file_embeddings.file_id
                  AND files.user_id = auth.uid()
            )
        )
        """
    )


def _drop_rls() -> None:
    op.execute("DROP POLICY IF EXISTS file_embeddings_isolation ON file_embeddings")
    op.execute("ALTER TABLE file_embeddings DISABLE ROW LEVEL SECURITY")
    op.execute("DROP POLICY IF EXISTS messages_isolation ON messages")
    op.execute("ALTER TABLE messages DISABLE ROW LEVEL SECURITY")

    for table_name in USER_SCOPED_TABLES:
        op.execute(f"DROP POLICY IF EXISTS {table_name}_isolation ON {table_name}")
        op.execute(f"ALTER TABLE {table_name} DISABLE ROW LEVEL SECURITY")

    op.execute("DROP POLICY IF EXISTS users_isolation ON users")
    op.execute("ALTER TABLE users DISABLE ROW LEVEL SECURITY")
