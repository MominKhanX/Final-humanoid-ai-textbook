"""
Indexing Job Tracker Service
Tracks textbook chapter indexing progress in Postgres
"""

from typing import Optional, List, Dict
from src.database.connection import db


async def create_indexing_job(chapter_id: str) -> int:
    """
    Create a new indexing job

    Args:
        chapter_id: Chapter identifier (e.g., "module-1-chapter-1")

    Returns:
        Job ID
    """
    job_id = await db.fetchval(
        """
        INSERT INTO indexing_jobs (chapter_id, status)
        VALUES ($1, 'pending')
        ON CONFLICT (chapter_id) DO UPDATE
        SET status = 'pending', started_at = NOW(), completed_at = NULL
        RETURNING job_id
        """,
        chapter_id,
    )
    return job_id


async def start_indexing_job(chapter_id: str):
    """Mark job as in progress"""
    await db.execute(
        """
        UPDATE indexing_jobs
        SET status = 'in_progress', started_at = NOW()
        WHERE chapter_id = $1
        """,
        chapter_id,
    )


async def complete_indexing_job(chapter_id: str, chunks_indexed: int):
    """Mark job as completed"""
    await db.execute(
        """
        UPDATE indexing_jobs
        SET status = 'completed', completed_at = NOW(), chunks_indexed = $1
        WHERE chapter_id = $2
        """,
        chunks_indexed,
        chapter_id,
    )


async def fail_indexing_job(chapter_id: str, error_message: str):
    """Mark job as failed"""
    await db.execute(
        """
        UPDATE indexing_jobs
        SET status = 'failed', completed_at = NOW(), error_message = $1
        WHERE chapter_id = $2
        """,
        error_message,
        chapter_id,
    )


async def get_indexing_status() -> List[Dict]:
    """Get status of all indexing jobs"""
    rows = await db.fetch(
        """
        SELECT chapter_id, status, started_at, completed_at, chunks_indexed, error_message
        FROM indexing_jobs
        ORDER BY started_at DESC
        """
    )

    return [
        {
            "chapter_id": row["chapter_id"],
            "status": row["status"],
            "started_at": row["started_at"].isoformat() if row["started_at"] else None,
            "completed_at": row["completed_at"].isoformat()
            if row["completed_at"]
            else None,
            "chunks_indexed": row["chunks_indexed"],
            "error_message": row["error_message"],
        }
        for row in rows
    ]


async def get_completed_chapters() -> List[str]:
    """Get list of successfully indexed chapters"""
    rows = await db.fetch(
        """
        SELECT chapter_id
        FROM indexing_jobs
        WHERE status = 'completed'
        ORDER BY completed_at DESC
        """
    )

    return [row["chapter_id"] for row in rows]
