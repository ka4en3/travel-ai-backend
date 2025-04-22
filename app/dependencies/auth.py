from models import User


async def get_current_user() -> User:
    return User(telegram_id=1)
