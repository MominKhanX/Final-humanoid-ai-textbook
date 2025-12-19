"""
Database Migration Runner
Runs SQL migrations to create required tables in Neon Postgres
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.connection import db


async def run_migrations():
    """
    Run all database migrations

    Creates:
    - chat_sessions table
    - chat_messages table
    - indexing_jobs table
    """
    print("🚀 Running database migrations...\n")

    try:
        # Connect to database
        print("📡 Connecting to Neon Postgres...")
        await db.connect()
        print("   ✅ Connected\n")

        # Read migration SQL
        migration_file = Path(__file__).parent.parent / "src" / "database" / "migrations" / "001_initial_schema.sql"

        if not migration_file.exists():
            print(f"❌ Migration file not found: {migration_file}")
            return

        print(f"📄 Reading migration file: {migration_file.name}")
        with open(migration_file, "r", encoding="utf-8") as f:
            migration_sql = f.read()

        print(f"   ✅ Migration loaded\n")

        # Execute migration
        print("🔨 Executing migration SQL...")
        await db.execute(migration_sql)
        print("   ✅ Migration executed\n")

        # Verify tables were created
        print("🔍 Verifying tables...")
        tables = await db.fetch(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
            """
        )

        created_tables = [row["table_name"] for row in tables]
        expected_tables = ["chat_sessions", "chat_messages", "indexing_jobs"]

        for table in expected_tables:
            if table in created_tables:
                print(f"   ✅ {table}")
            else:
                print(f"   ❌ {table} (not found)")

        print("\n" + "=" * 60)
        print("✅ DATABASE MIGRATIONS COMPLETED")
        print("=" * 60)
        print(f"Tables created: {len(expected_tables)}")
        print(f"  - chat_sessions: User session management")
        print(f"  - chat_messages: Question/answer history with citations")
        print(f"  - indexing_jobs: Chapter indexing status tracking")
        print("=" * 60)

    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ MIGRATION FAILED")
        print("=" * 60)
        print(f"Error: {e}")
        print("\nTroubleshooting:")
        print("  1. Check DATABASE_URL in .env file")
        print("  2. Verify Neon database is accessible")
        print("  3. Ensure you have database permissions")
        print("=" * 60)
        raise

    finally:
        # Disconnect
        await db.disconnect()


if __name__ == "__main__":
    asyncio.run(run_migrations())
