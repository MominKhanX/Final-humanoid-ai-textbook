"""
Neon Serverless Postgres connection management with asyncpg
Provides connection pooling for concurrent request handling
"""

import asyncpg
from typing import Optional
from src.config import settings


class DatabaseConnection:
    """Manages PostgreSQL connection pool"""

    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        """Initialize connection pool"""
        if self.pool is None:
            self.pool = await asyncpg.create_pool(
                dsn=settings.database_url,
                min_size=5,
                max_size=20,
                command_timeout=60,
            )
            print("[OK] Connected to Neon Postgres")

    async def disconnect(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()
            print("[OK] Disconnected from Neon Postgres")

    async def execute(self, query: str, *args):
        """Execute a query without returning results"""
        async with self.pool.acquire() as connection:
            return await connection.execute(query, *args)

    async def fetch(self, query: str, *args):
        """Fetch multiple rows"""
        async with self.pool.acquire() as connection:
            return await connection.fetch(query, *args)

    async def fetchrow(self, query: str, *args):
        """Fetch a single row"""
        async with self.pool.acquire() as connection:
            return await connection.fetchrow(query, *args)

    async def fetchval(self, query: str, *args):
        """Fetch a single value"""
        async with self.pool.acquire() as connection:
            return await connection.fetchval(query, *args)


# Global database connection instance
db = DatabaseConnection()
