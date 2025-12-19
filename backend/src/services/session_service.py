"""
Chat Session Service
Manages user conversation sessions in Neon Postgres
"""

from typing import Optional
import uuid
from datetime import datetime
from src.database.connection import db


async def create_session(user_id: Optional[str] = None) -> str:
    """
    Create a new chat session

    Args:
        user_id: Optional user identifier for future auth

    Returns:
        Session UUID as string
    """
    session_id = str(uuid.uuid4())

    await db.execute(
        """
        INSERT INTO chat_sessions (session_id, user_id)
        VALUES ($1, $2)
        """,
        uuid.UUID(session_id),
        uuid.UUID(user_id) if user_id else None,
    )

    return session_id


async def get_session(session_id: str) -> Optional[dict]:
    """
    Retrieve session information

    Args:
        session_id: Session UUID

    Returns:
        Session data or None if not found
    """
    try:
        row = await db.fetchrow(
            """
            SELECT session_id, created_at, last_activity, user_id
            FROM chat_sessions
            WHERE session_id = $1
            """,
            uuid.UUID(session_id),
        )

        if row:
            return {
                "session_id": str(row["session_id"]),
                "created_at": row["created_at"].isoformat(),
                "last_activity": row["last_activity"].isoformat(),
                "user_id": str(row["user_id"]) if row["user_id"] else None,
            }
        return None
    except Exception as e:
        print(f"✗ Failed to get session: {e}")
        return None


async def update_last_activity(session_id: str):
    """
    Update session's last activity timestamp

    Args:
        session_id: Session UUID
    """
    await db.execute(
        """
        UPDATE chat_sessions
        SET last_activity = NOW()
        WHERE session_id = $1
        """,
        uuid.UUID(session_id),
    )


async def session_exists(session_id: str) -> bool:
    """
    Check if session exists

    Args:
        session_id: Session UUID

    Returns:
        True if session exists, False otherwise
    """
    try:
        result = await db.fetchval(
            """
            SELECT EXISTS(
                SELECT 1 FROM chat_sessions WHERE session_id = $1
            )
            """,
            uuid.UUID(session_id),
        )
        return result
    except:
        return False
