# app/fixtures/load_with_services.py

import asyncio
import logging

from db.sessions import async_session_factory
from services.crud.user_service import UserService
from services.crud.route_service import RouteService
from services.crud.route_access_service import RouteAccessService
from repositories import (
    UserRepository,
    RouteRepository,
    AICacheRepository,
    RouteAccessRepository,
)
from schemas.user import UserCreate
from schemas.route import RouteCreate, RouteGenerateRequest
from schemas.route_access import RouteAccessCreate
from schemas.ai_cache import AICacheCreate
from constants.roles import RouteRole

from .data_for_services import (
    USERS_FIXTURES,
    ROUTES_FIXTURES,
    AICACHE_FIXTURES,
    ROUTE_ACCESS_FIXTURES,
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def load_users(session):
    repo = UserRepository(session)
    service = UserService(repo)

    logger.info("🔧 Loading user fixtures via UserService...")
    for data in USERS_FIXTURES:
        user_in = UserCreate(**data)
        try:
            user = await service.register(user_in)
            logger.info("✅ Created User id=%s", user.id)

            if user.email and "password" in data:
                token = await service.authenticate(user.email, data["password"])
                logger.info("🪙 Token for %s: %s", user.email, token.access_token)

        except Exception as e:
            logger.error("❌ Skipping user %s: %s", data, e)


async def load_ai_cache(session):
    repo = AICacheRepository(session)

    logger.info("🔧 Loading AI-cache fixtures via AICacheRepository…")
    for data in AICACHE_FIXTURES:
        try:
            cache = await repo.create(AICacheCreate(**data))
            logger.info("✅ Created AICache id=%s key=%s", cache.id, cache.cache_key)
        except Exception as e:
            logger.error("❌ Skipping AICache %r: %s", data.get("cache_key"), e)


async def load_routes(session):
    route_repo = RouteRepository(session)
    user_repo = UserRepository(session)
    cache_repo = AICacheRepository(session)
    access_repo = RouteAccessRepository(session)
    service = RouteService(route_repo, user_repo, cache_repo, access_repo)

    logger.info("🔧 Loading route fixtures via RouteService...")
    for data in ROUTES_FIXTURES:
        route_in = RouteGenerateRequest(**data)
        try:
            user = await user_repo.get_by_telegram_id(100001)
            if user:
                route = await service.create_route(route_in, user.id)
            logger.info("✅ Created Route id=%s code=%s", route.id, route.share_code)
        except Exception as e:
            logger.error("❌ Skipping route %s: %s", data.get("name"), e)


async def load_extra_access(session):
    access_repo = RouteAccessRepository(session)
    route_repo = RouteRepository(session)
    service = RouteAccessService(access_repo, route_repo)

    logger.info("🔧 Loading additional route_access fixtures via RouteAccessService...")
    for data in ROUTE_ACCESS_FIXTURES:
        access_in = RouteAccessCreate(**data)
        try:
            await service.grant_access(access_in)
            logger.info(
                "✅ Granted %s access to user_id=%s on route_id=%s",
                access_in.role,
                access_in.user_id,
                access_in.route_id,
            )
        except Exception as e:
            logger.error("❌ Skipping access %s: %s", (access_in.user_id, access_in.route_id), e)


async def load_all():
    logger.info("🚀 Seeding data via service layer...")
    async with async_session_factory() as session:
        try:
            await load_users(session)
            await load_ai_cache(session)
            await load_routes(session)
            await load_extra_access(session)
            await session.commit()
        except Exception:
            logger.exception("❌ Seeding failed, rolling back")
            await session.rollback()
        else:
            logger.info("🎉 Seeding complete")


if __name__ == "__main__":
    asyncio.run(load_all())
