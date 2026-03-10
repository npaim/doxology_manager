"""create service_moments

Revision ID: c0ffee5e1f01
Revises: a1b2c3d4e5f6
Create Date: 2026-03-10 00:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c0ffee5e1f01'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'service_moments',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('service_id', sa.Integer(), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('responsible', sa.String(), nullable=True),
        sa.Column('time', sa.Time(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['service_id'], ['services.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_service_moments_service_id', 'service_moments', ['service_id'])


def downgrade() -> None:
    op.drop_index('ix_service_moments_service_id', table_name='service_moments')
    op.drop_table('service_moments')
