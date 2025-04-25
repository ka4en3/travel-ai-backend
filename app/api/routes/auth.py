# app/api/routes/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from repositories.user import UserRepository
from services.auth_service import AuthService
from schemas.token import Token
from db.sessions import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user import UserCreate
from utils.security import hash_password

router = APIRouter(tags=["Auth"])


@router.post("/auth/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_session)):
    user_repo = UserRepository(session)
    auth_svc = AuthService(user_repo)
    try:
        token = await auth_svc.authenticate(form_data.username, form_data.password)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    return {"access_token": token}


@router.post("/auth/register", response_model=None, status_code=201)
async def register(user_in: UserCreate, session: AsyncSession = Depends(get_session)):
    # здесь можно использовать UserService, но нужно захэшировать пароль
    from repositories.user import UserRepository

    repo = UserRepository(session)
    user = user_in.model_dump()
    user["password_hash"] = hash_password(user_in.password)  # добавьте поле password в UserCreate!
    await repo.create(UserCreate(**user))
