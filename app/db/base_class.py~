from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import declared_attr
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from app.core.config import convention


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=convention)

    id: Mapped[int] = mapped_column(primary_key=True, index=True, nullable=False)

    # @declared_attr.directive
    # def __tablename__(cls) -> str:
    #     return f"{cls.__name__.lower()}s"
