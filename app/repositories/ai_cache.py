# app/repositories/ai_cache.py

import logging
from typing import Optional
from datetime import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from models.ai_cache import AICache
from schemas.ai_cache import AICacheCreate
from .base import BaseRepository

logger = logging.getLogger(__name__)


class AICacheRepository(BaseRepository[AICache]):
    """
    Repository for working with AICache entries.
    Extends BaseRepository and adds methods specific to caching logic.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(AICache, session)

    async def get_by_hash(self, prompt_hash: str) -> Optional[AICache]:
        """
        Get an AICache entry by prompt hash (used for caching).
        """
        logger.debug("AICache Repo: fetching AICache by prompt_hash=%s", prompt_hash)
        stmt = select(AICache).where(AICache.prompt_hash == prompt_hash)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_cache_key(self, cache_key: str) -> Optional[AICache]:
        """
        Get an AICache entry by its full cache_key.
        """
        logger.debug("AICache Repo: fetching by cache_key=%s", cache_key)
        stmt = select(AICache).where(AICache.cache_key == cache_key)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_similar(
        self,
        origin: str,
        destination: str,
        duration_days: int,
        budget: float,
    ) -> Optional[AICache]:
        """
        Find an entry matching the same parameters (origin, destination, days, budget).
        """
        logger.debug(
            "AICache Repo: fetching by params origin=%s, destination=%s, days=%s, budget=%s",
            origin,
            destination,
            duration_days,
            budget,
        )
        stmt = select(AICache).where(
            AICache.origin == origin,
            AICache.destination == destination,
            AICache.duration_days == duration_days,
            AICache.budget == budget,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, obj_in: AICacheCreate) -> AICache:
        """
        Create a new cache entry.
        """
        logger.info("AICache Repo: creating new cache entry")
        data = obj_in.model_dump()
        # compute cache_key = f"{origin}:{destination}:{days}:{budget}"
        data["cache_key"] = f"{data['origin']}:{data['destination']}:{data['duration_days']}:{data['budget']}"
        new_cache = AICache(**data)
        self.session.add(new_cache)
        try:
            await self.session.commit()
            await self.session.refresh(new_cache)
            logger.info("AICache Repo: created id=%s", new_cache.id)
            return new_cache
        except IntegrityError as e:
            logger.warning("AICache Repo: IntegrityError on create: %s", e)
            await self.session.rollback()
            raise

    async def increment_hit_count(self, cache_id: int) -> None:
        """
        Atomically increment hit_count and update expires_at.
        """
        logger.debug("AICache Repo: incrementing hit_count for id=%s", cache_id)
        stmt = (
            update(AICache)
            .where(AICache.id == cache_id)
            .values(
                hit_count=AICache.hit_count + 1,
                # optional: refresh expires_at, e.g., extend expiration by 1h
                # expires_at=func.now() + text("interval '1 hour'")
            )
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def delete_expired(self, before: Optional[datetime] = None) -> int:
        """
        Delete all cache entries with expires_at <= now (or `before` if provided).
        Returns the number of rows deleted.
        """
        cutoff = before or datetime.utcnow()
        logger.info("AICache Repo: deleting expired entries before %s", cutoff)
        stmt = delete(AICache).where(AICache.expires_at != None, AICache.expires_at <= cutoff)
        result = await self.session.execute(stmt)
        await self.session.commit()
        deleted = result.rowcount or 0
        logger.info("AICache Repo: deleted %d expired entries", deleted)
        return deleted
