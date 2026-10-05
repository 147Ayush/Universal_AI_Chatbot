# backend/app/db/base.py
"""SQLAlchemy declarative base — every ORM model inherits from this."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
