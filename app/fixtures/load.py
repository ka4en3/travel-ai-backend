# app/fixtures/load.py

import asyncio
import logging
from db.sessions import async_session_factory

from models import User, AICache, Route, RouteDay, Activity, RouteAccess
from .data import (
    USERS_FIXTURES,
    AICACHE_FIXTURES,
    ROUTES_FIXTURES,
    ROUTE_DAYS_FIXTURES,
    ACTIVITIES_FIXTURES,
    ROUTE_ACCESS_FIXTURES,
    # EXPORTS_FIXTURES
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def load_fixtures(session, model, fixtures, label: str = ""):
    for data in fixtures:
        obj = model(**data)
        session.add(obj)
        logger.info("Added %s: %s", label or model.__name__, repr(obj))


async def load_all():
    logger.info("Seeding data...")
    async with async_session_factory() as session:
        try:
            await load_fixtures(session, User, USERS_FIXTURES, label="User")
            await load_fixtures(session, AICache, AICACHE_FIXTURES, label="AICache")
            await load_fixtures(session, Route, ROUTES_FIXTURES, label="Route")
            await load_fixtures(session, RouteDay, ROUTE_DAYS_FIXTURES, label="RouteDay")
            await load_fixtures(session, Activity, ACTIVITIES_FIXTURES, label="Activity")
            await load_fixtures(session, RouteAccess, ROUTE_ACCESS_FIXTURES, label="RouteAccess")
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error("Seeding failed: %s", e)
    logger.info("Seeding complete.")


if __name__ == "__main__":
    asyncio.run(load_all())
