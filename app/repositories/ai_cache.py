# app/repositories/ai_cache.py

import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.ai_cache import AICache
from db.base_class import Base
from .base import BaseRepository

logger = logging.getLogger(__name__)


class AICacheRepository(BaseRepository[AICache]):
    """
    Repository for working with AICache entries.
    """

    model = AICache

    def __init__(self, session: AsyncSession):
        super().__init__(AICache, session)

    async def get(self, id: int) -> Optional[AICache]:
        """
        Get a single AICache entry by its ID.
        """
        logger.debug("Fetching AICache by id=%s", id)
        stmt = select(AICache).where(AICache.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_hash(self, prompt_hash: str) -> Optional[AICache]:
        """
        Get an AICache entry by prompt hash (used for caching).
        """
        logger.debug("Fetching AICache by prompt_hash=%s", prompt_hash)
        stmt = select(AICache).where(AICache.prompt_hash == prompt_hash)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
