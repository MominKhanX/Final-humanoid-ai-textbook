# Data Model: RAG Chatbot Backend

**Feature**: 002-rag-chatbot-backend
**Date**: 2025-12-16
**Status**: Complete

## Overview

This document defines the data entities, relationships, and schemas for the RAG Chatbot Backend system. All entities are designed to support the constitution requirements: <3s response time, context-aware conversations, source citations, and concurrent user support.

---

## Entity Relationship Diagram

```
┌─────────────────┐         ┌──────────────────┐
│  ChatSession    │1      * │  ChatMessage     │
│─────────────────│◄────────│──────────────────│
│ session_id (PK) │         │ message_id (PK)  │
│ created_at      │         │ session_id (FK)  │
│ last_activity   │         │ question         │
│ user_id (opt)   │         │ answer           │
└─────────────────┘         │ cited_sources    │
                            │ timestamp        │
                            │ response_time_ms │
                            └──────────────────┘

┌──────────────────┐
│ IndexingJob      │
│──────────────────│
│ job_id (PK)      │
│ chapter_id       │
│ status           │
│ started_at       │
│ completed_at     │
│ error_message    │
└──────────────────┘

┌──────────────────┐ (Qdrant Vector DB)
│ TextbookChunk    │
│──────────────────│
│ chunk_id (PK)    │
│ embedding (vec)  │
│ module_id        │
│ chapter_id       │
│ section_title    │
│ content          │
│ content_type     │
│ page_number      │
└──────────────────┘
```

---

## 1. ChatSession

**Purpose**: Tracks user conversation sessions for multi-turn dialogue support

**Storage**: Neon Serverless Postgres

**Schema**:
```sql
CREATE TABLE chat_sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    user_id UUID NULL,  -- Optional for future authentication integration
    CONSTRAINT chk_activity_after_creation CHECK (last_activity >= created_at)
);

-- Index for session cleanup queries
CREATE INDEX idx_chat_sessions_last_activity ON chat_sessions(last_activity DESC);

-- Index for user queries (future auth)
CREATE INDEX idx_chat_sessions_user_id ON chat_sessions(user_id) WHERE user_id IS NOT NULL;
```

**Fields**:
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `session_id` | UUID | PRIMARY KEY | Unique identifier for the conversation session |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Session creation timestamp |
| `last_activity` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Last message timestamp (updated on each message) |
| `user_id` | UUID | NULLABLE | Optional user identifier for future authentication |

**Relationships**:
- **Has Many**: `ChatMessage` (one session contains multiple messages)

**Validation Rules**:
- `session_id` MUST be a valid UUIDv4
- `last_activity` MUST be >= `created_at`
- Sessions with `last_activity` > 24 hours old SHOULD be archived/deleted

**State Transitions**:
```
┌─────────┐  create  ┌────────┐  24h inactivity  ┌──────────┐
│ None    │─────────►│ Active │─────────────────►│ Expired  │
└─────────┘          └────────┘                   └──────────┘
                         │  ▲
                         │  │ update on each message
                         └──┘
```

**Indexes**:
- `idx_chat_sessions_last_activity`: Speeds up session cleanup queries
- `idx_chat_sessions_user_id`: Supports future user-based session retrieval

---

## 2. ChatMessage

**Purpose**: Stores individual question-answer exchanges with citations and performance metrics

**Storage**: Neon Serverless Postgres

**Schema**:
```sql
CREATE TABLE chat_messages (
    message_id SERIAL PRIMARY KEY,
    session_id UUID NOT NULL,
    question TEXT NOT NULL CHECK (char_length(question) <= 1000),
    answer TEXT NOT NULL,
    cited_sources JSONB NOT NULL DEFAULT '[]'::jsonb,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    response_time_ms INTEGER NOT NULL CHECK (response_time_ms > 0),
    CONSTRAINT fk_session
        FOREIGN KEY(session_id)
        REFERENCES chat_sessions(session_id)
        ON DELETE CASCADE
);

-- Index for retrieving conversation history (most recent first)
CREATE INDEX idx_chat_messages_session_timestamp
    ON chat_messages(session_id, timestamp DESC);

-- Index for performance analysis
CREATE INDEX idx_chat_messages_response_time
    ON chat_messages(response_time_ms);
```

**Fields**:
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `message_id` | SERIAL | PRIMARY KEY | Auto-incrementing message identifier |
| `session_id` | UUID | FOREIGN KEY, NOT NULL | Reference to parent session |
| `question` | TEXT | NOT NULL, max 1000 chars | Student's question text |
| `answer` | TEXT | NOT NULL | AI-generated response |
| `cited_sources` | JSONB | NOT NULL, DEFAULT [] | Array of source citations (see structure below) |
| `timestamp` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Message creation timestamp |
| `response_time_ms` | INTEGER | NOT NULL, > 0 | Time taken to generate response (ms) |

**JSONB Structure for `cited_sources`**:
```json
[
    {
        "module_id": "module-1-ros2",
        "chapter_id": "chapter-1",
        "section_title": "Introduction to ROS 2 Nodes",
        "url": "/docs/module-1-ros2/chapter-1#ros2-nodes",
        "relevance_score": 0.92
    },
    {
        "module_id": "module-1-ros2",
        "chapter_id": "chapter-2",
        "section_title": "Node Communication Patterns",
        "url": "/docs/module-1-ros2/chapter-2#communication",
        "relevance_score": 0.85
    }
]
```

**Relationships**:
- **Belongs To**: `ChatSession` (via `session_id`)

**Validation Rules**:
- `question` length MUST be <= 1000 characters (enforced by CHECK constraint)
- `answer` MUST NOT be empty
- `cited_sources` MUST be a valid JSON array (can be empty `[]`)
- `response_time_ms` MUST be > 0
- `timestamp` MUST be >= parent session's `created_at`

**Indexes**:
- `idx_chat_messages_session_timestamp`: Optimizes history retrieval (GET `/chat/history`)
- `idx_chat_messages_response_time`: Enables performance monitoring queries

**Performance Considerations**:
- JSONB for `cited_sources` allows efficient querying (e.g., "find all messages citing Module 2")
- Partition table by `timestamp` if messages exceed 1M records (future optimization)

---

## 3. TextbookChunk

**Purpose**: Stores vectorized textbook content for semantic search

**Storage**: Qdrant Cloud Vector Database

**Collection Configuration**:
```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"))

# Create collection
client.create_collection(
    collection_name="textbook_chunks",
    vectors_config=VectorParams(
        size=1536,  # text-embedding-3-small dimension
        distance=Distance.COSINE  # Best for OpenAI embeddings
    )
)
```

**Point Structure** (each chunk is a "point" in Qdrant):
```python
{
    "id": "chunk_uuid",  # Unique identifier
    "vector": [0.123, -0.456, ...],  # 1536-dimensional embedding
    "payload": {
        "chunk_id": "mod1_ch1_sec1_p1",
        "module_id": "module-1-ros2",
        "chapter_id": "chapter-1",
        "section_title": "Introduction to ROS 2 Nodes",
        "content": "A ROS 2 node is a process that performs computation...",
        "content_type": "text",  # Enum: text | code | diagram
        "page_number": 12,
        "chunk_index": 1,  # Position within chapter
        "token_count": 487
    }
}
```

**Payload Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `chunk_id` | string | Human-readable identifier (format: `{module}_{chapter}_{section}_{index}`) |
| `module_id` | string | Module identifier (e.g., "module-1-ros2") |
| `chapter_id` | string | Chapter identifier (e.g., "chapter-1") |
| `section_title` | string | Section heading for context |
| `content` | string | Actual text content (500-1000 tokens) |
| `content_type` | keyword | Type of content: `text`, `code`, `diagram` |
| `page_number` | integer | Page number in textbook (for citation) |
| `chunk_index` | integer | Position of chunk within chapter |
| `token_count` | integer | Number of tokens in chunk |

**Validation Rules**:
- `chunk_id` MUST be unique across all chunks
- `content` MUST be non-empty and <= 1000 tokens
- `content_type` MUST be one of: `text`, `code`, `diagram`
- `module_id` and `chapter_id` MUST follow naming convention

**Search Filters** (Qdrant supports metadata filtering):
```python
# Filter by module
search_params = SearchParams(
    filter={
        "must": [
            {"key": "module_id", "match": {"value": "module-1-ros2"}}
        ]
    }
)

# Filter by content type (e.g., only search code blocks)
search_params = SearchParams(
    filter={
        "must": [
            {"key": "content_type", "match": {"value": "code"}}
        ]
    }
)
```

**Performance Characteristics**:
- **Search Latency**: <100ms for 1M vectors (Qdrant benchmark)
- **Storage**: ~6MB per 1k chunks (1536 floats × 4 bytes × 1000)
- **Indexing**: ~200ms per chunk (embedding generation)

---

## 4. IndexingJob

**Purpose**: Tracks chapter indexing progress for monitoring and troubleshooting

**Storage**: Neon Serverless Postgres

**Schema**:
```sql
CREATE TYPE indexing_status AS ENUM ('pending', 'in_progress', 'completed', 'failed');

CREATE TABLE indexing_jobs (
    job_id SERIAL PRIMARY KEY,
    chapter_id VARCHAR(50) NOT NULL UNIQUE,
    status indexing_status NOT NULL DEFAULT 'pending',
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    chunks_indexed INTEGER DEFAULT 0,
    total_chunks INTEGER DEFAULT 0,
    CONSTRAINT chk_completion CHECK (
        (status = 'completed' AND completed_at IS NOT NULL) OR
        (status != 'completed')
    ),
    CONSTRAINT chk_progress CHECK (chunks_indexed <= total_chunks)
);

-- Index for status queries
CREATE INDEX idx_indexing_jobs_status ON indexing_jobs(status);

-- Index for chapter lookup
CREATE INDEX idx_indexing_jobs_chapter_id ON indexing_jobs(chapter_id);
```

**Fields**:
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `job_id` | SERIAL | PRIMARY KEY | Auto-incrementing job identifier |
| `chapter_id` | VARCHAR(50) | UNIQUE, NOT NULL | Chapter being indexed (e.g., "module-1_chapter-1") |
| `status` | ENUM | NOT NULL, DEFAULT 'pending' | Current job status |
| `started_at` | TIMESTAMP WITH TIME ZONE | NULLABLE | Job start time |
| `completed_at` | TIMESTAMP WITH TIME ZONE | NULLABLE | Job completion time |
| `error_message` | TEXT | NULLABLE | Error details if failed |
| `chunks_indexed` | INTEGER | DEFAULT 0 | Number of chunks successfully indexed |
| `total_chunks` | INTEGER | DEFAULT 0 | Total chunks to index |

**Status Enum Values**:
- `pending`: Job created but not started
- `in_progress`: Currently indexing
- `completed`: Successfully finished
- `failed`: Encountered error during indexing

**State Transitions**:
```
┌─────────┐  start  ┌─────────────┐  success  ┌───────────┐
│ pending │────────►│ in_progress │──────────►│ completed │
└─────────┘         └─────────────┘            └───────────┘
                         │
                         │ error
                         ▼
                    ┌────────┐
                    │ failed │
                    └────────┘
```

**Validation Rules**:
- `completed_at` MUST be NULL unless `status = 'completed'`
- `chunks_indexed` MUST be <= `total_chunks`
- `error_message` SHOULD be populated when `status = 'failed'`

**Indexes**:
- `idx_indexing_jobs_status`: Speeds up "find all failed jobs" queries
- `idx_indexing_jobs_chapter_id`: Supports "check if chapter is indexed" lookups

**Usage Example**:
```sql
-- Check indexing progress
SELECT
    chapter_id,
    status,
    ROUND(100.0 * chunks_indexed / NULLIF(total_chunks, 0), 2) AS progress_pct
FROM indexing_jobs
WHERE status = 'in_progress';

-- Find failed jobs
SELECT chapter_id, error_message, started_at
FROM indexing_jobs
WHERE status = 'failed'
ORDER BY started_at DESC;
```

---

## Data Flow Diagram

### Chat Request Flow:
```
┌────────┐   1. POST /chat    ┌──────────────┐   2. Generate    ┌─────────┐
│ Client │──────────────────► │  FastAPI     │   embedding      │ OpenAI  │
└────────┘                    │  Endpoint    │◄─────────────────┤ API     │
                              └──────────────┘                   └─────────┘
                                     │  ▲
                           3. Search │  │ 6. Save message
                              chunks │  │    + update session
                                     ▼  │
                              ┌──────────────┐                   ┌──────────┐
                              │   Qdrant     │   4. Generate    │ Postgres │
                              │  (Vectors)   │   answer with    │ (History)│
                              └──────────────┘   retrieved      └──────────┘
                                     │           context             ▲
                                     │                               │
                                     └───────────────────────────────┘
                                            5. LLM call (GPT-4)
```

### Indexing Flow:
```
┌────────────┐   1. Read      ┌──────────────┐   2. Chunk &     ┌─────────┐
│ Textbook   │   chapters     │  Indexing    │   embed content  │ OpenAI  │
│ MDX Files  │───────────────►│  Script      │◄─────────────────┤ API     │
└────────────┘                └──────────────┘                   └─────────┘
                                     │  │
                           3. Upload │  │ 4. Update
                              vectors│  │    job status
                                     ▼  ▼
                              ┌──────────────┐                   ┌──────────┐
                              │   Qdrant     │                   │ Postgres │
                              │  (Vectors)   │                   │ (Jobs)   │
                              └──────────────┘                   └──────────┘
```

---

## Database Migrations

**Tool**: Alembic (async-compatible)

**Migration Example** (Initial schema):
```python
# alembic/versions/001_initial_schema.py
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

def upgrade():
    # Create chat_sessions table
    op.create_table(
        'chat_sessions',
        sa.Column('session_id', UUID, primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('last_activity', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('user_id', UUID, nullable=True),
        sa.CheckConstraint('last_activity >= created_at', name='chk_activity_after_creation')
    )
    op.create_index('idx_chat_sessions_last_activity', 'chat_sessions', ['last_activity'], postgresql_using='btree')

    # Create chat_messages table
    op.create_table(
        'chat_messages',
        sa.Column('message_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('session_id', UUID, nullable=False),
        sa.Column('question', sa.Text, nullable=False),
        sa.Column('answer', sa.Text, nullable=False),
        sa.Column('cited_sources', JSONB, nullable=False, server_default='[]'),
        sa.Column('timestamp', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('response_time_ms', sa.Integer, nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['chat_sessions.session_id'], ondelete='CASCADE'),
        sa.CheckConstraint("char_length(question) <= 1000", name='chk_question_length'),
        sa.CheckConstraint("response_time_ms > 0", name='chk_positive_response_time')
    )
    op.create_index('idx_chat_messages_session_timestamp', 'chat_messages', ['session_id', sa.text('timestamp DESC')])

    # Create indexing_jobs table
    op.execute("CREATE TYPE indexing_status AS ENUM ('pending', 'in_progress', 'completed', 'failed')")
    op.create_table(
        'indexing_jobs',
        sa.Column('job_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('chapter_id', sa.VARCHAR(50), nullable=False, unique=True),
        sa.Column('status', sa.Enum('pending', 'in_progress', 'completed', 'failed', name='indexing_status'), nullable=False, server_default='pending'),
        sa.Column('started_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('completed_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('error_message', sa.Text),
        sa.Column('chunks_indexed', sa.Integer, server_default='0'),
        sa.Column('total_chunks', sa.Integer, server_default='0'),
        sa.CheckConstraint("(status = 'completed' AND completed_at IS NOT NULL) OR (status != 'completed')", name='chk_completion'),
        sa.CheckConstraint("chunks_indexed <= total_chunks", name='chk_progress')
    )
    op.create_index('idx_indexing_jobs_status', 'indexing_jobs', ['status'])

def downgrade():
    op.drop_table('chat_messages')
    op.drop_table('chat_sessions')
    op.drop_table('indexing_jobs')
    op.execute('DROP TYPE indexing_status')
```

---

## Data Retention & Archival

**Session Cleanup**:
```sql
-- Delete sessions inactive for >24 hours
DELETE FROM chat_sessions
WHERE last_activity < NOW() - INTERVAL '24 hours';

-- Archive old sessions (move to cold storage)
INSERT INTO archived_sessions
SELECT * FROM chat_sessions
WHERE last_activity < NOW() - INTERVAL '30 days';

DELETE FROM chat_sessions
WHERE session_id IN (SELECT session_id FROM archived_sessions);
```

**Automatic Cleanup Job** (Run daily via cron):
```python
# cleanup_sessions.py
import asyncpg
import os
from datetime import datetime, timedelta

async def cleanup_old_sessions():
    conn = await asyncpg.connect(os.getenv("DATABASE_URL"))
    cutoff_time = datetime.utcnow() - timedelta(hours=24)

    deleted = await conn.execute(
        "DELETE FROM chat_sessions WHERE last_activity < $1",
        cutoff_time
    )
    print(f"Deleted {deleted} expired sessions")
    await conn.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(cleanup_old_sessions())
```

---

## Summary

**Entity Count**: 4 entities (ChatSession, ChatMessage, TextbookChunk, IndexingJob)

**Storage Distribution**:
- **Postgres (Neon)**: 3 tables (sessions, messages, indexing_jobs)
- **Qdrant**: 1 collection (textbook_chunks)

**Total Storage Estimate** (23 chapters):
- Textbook chunks: ~500 chunks × 6KB = **~3MB** (Qdrant)
- Chat messages: ~1000 messages × 2KB = **~2MB** (Postgres)
- Sessions: ~100 active × 100B = **~10KB** (Postgres)
- **Total**: ~5MB (well within free tiers)

**Performance Validation**:
- Session lookup: <10ms (indexed UUID primary key)
- History retrieval: <50ms (indexed session_id + timestamp)
- Vector search: <100ms (Qdrant optimized)
- **Total data access**: <160ms ✅ (within 3s budget)

This data model supports all constitution requirements while staying within free tier limits.
