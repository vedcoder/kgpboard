"""categories as enums; event registration_url and target_year

Revision ID: 914c4e12f0b3
Revises: 343f7695b561
Create Date: 2026-07-05 18:53:03.093666

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '914c4e12f0b3'
down_revision: Union[str, Sequence[str], None] = '343f7695b561'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


notice_category = sa.Enum(
    "Academic", "Examination", "Placement", "Hostel", "Scholarship", "General",
    name="notice_category",
)
event_category = sa.Enum(
    "Workshop", "Talk", "Cultural", "Sports", "Placement", "Fest",
    name="event_category",
)
target_year = sa.Enum(
    "All years", "1st year", "2nd year", "3rd year", "4th year", "5th year",
    name="target_year",
)


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    notice_category.create(bind, checkfirst=True)
    event_category.create(bind, checkfirst=True)
    target_year.create(bind, checkfirst=True)

    # Convert the free-text category columns to the new enum types. The USING
    # clause casts existing text values into the enum (tables are empty in dev).
    op.alter_column(
        "notices", "category",
        type_=notice_category,
        existing_type=sa.String(length=100),
        postgresql_using="category::text::notice_category",
        existing_nullable=False,
    )
    op.alter_column(
        "events", "category",
        type_=event_category,
        existing_type=sa.String(length=100),
        postgresql_using="category::text::event_category",
        existing_nullable=False,
    )

    op.add_column("events", sa.Column("registration_url", sa.String(length=500), nullable=True))
    op.add_column("events", sa.Column("target_year", target_year, nullable=True))
    op.create_index(op.f("ix_events_target_year"), "events", ["target_year"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_events_target_year"), table_name="events")
    op.drop_column("events", "target_year")
    op.drop_column("events", "registration_url")
    op.alter_column(
        "events", "category",
        type_=sa.String(length=100),
        existing_type=event_category,
        postgresql_using="category::text",
        existing_nullable=False,
    )
    op.alter_column(
        "notices", "category",
        type_=sa.String(length=100),
        existing_type=notice_category,
        postgresql_using="category::text",
        existing_nullable=False,
    )
    bind = op.get_bind()
    target_year.drop(bind, checkfirst=True)
    event_category.drop(bind, checkfirst=True)
    notice_category.drop(bind, checkfirst=True)
