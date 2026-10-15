from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from contextlib import asynccontextmanager
from backend.config import settings

checkpointer_instance: AsyncSqliteSaver = None


@asynccontextmanager
async def get_checkpointer():
    """Provides async context manager for SQLite checkpointing."""
    async with AsyncSqliteSaver.from_conn_string(settings.DATABASE_URL) as saver:
        yield saver