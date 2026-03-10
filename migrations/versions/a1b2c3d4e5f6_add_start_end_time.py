"""add start and end time to services

Revision ID: a1b2c3d4e5f6
Revises: 177313c788d7
Create Date: 2026-03-10 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '177313c788d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('services', sa.Column('start_time', sa.Time(), nullable=True))
    op.add_column('services', sa.Column('end_time', sa.Time(), nullable=True))
    # backfill
    op.execute('UPDATE services SET start_time = service_time WHERE service_time IS NOT NULL')
    op.execute('UPDATE services SET end_time = service_time WHERE service_time IS NOT NULL')


def downgrade() -> None:
    op.drop_column('services', 'end_time')
    op.drop_column('services', 'start_time')