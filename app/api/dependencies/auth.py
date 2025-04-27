# app/api/dependencies.py

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from db.sessions import get_session
from exceptions.user import UserNotFoundError
from repositories.user import UserRepository
from schemas.token import TokenPayload
from services.crud.user_service import UserService
from utils.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/auth/token")


async def get_user_service(session=Depends(get_session)) -> UserService:
    return UserService(UserRepository(session))


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    svc: UserService = Depends(get_user_service),
):
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = TokenPayload(**decode_access_token(token))
        # sub = payload.get("sub")
        sub = payload.sub
        if sub is None:
            raise credentials_exc
    except (JWTError, KeyError, ValueError):
        raise credentials_exc

    try:
        user = await svc.get_user_by_id(int(sub))
    except UserNotFoundError:
        raise credentials_exc

    return user
