"""Declarative base for all ORM models.

Every model class inherits from `Base`. SQLAlchemy collects them all onto
`Base.metadata`, which is the in-memory catalog of tables that Alembic reads
when generating migrations.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
