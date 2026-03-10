"""add members and moment member fk

Revision ID: baddcafe1234
Revises: c0ffee5e1f01
Create Date: 2026-03-10 00:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'baddcafe1234'
down_revision: Union[str, Sequence[str], None] = 'c0ffee5e1f01'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'members',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False, unique=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
    )
    op.add_column('service_moments', sa.Column('responsible_member_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_service_moments_member', 'service_moments', 'members', ['responsible_member_id'], ['id'], ondelete='SET NULL')
    op.create_index('ix_service_moments_member_id', 'service_moments', ['responsible_member_id'])


def downgrade() -> None:
    op.drop_index('ix_service_moments_member_id', table_name='service_moments')
    op.drop_constraint('fk_service_moments_member', 'service_moments', type_='foreignkey')
    op.drop_column('service_moments', 'responsible_member_id')
    op.drop_table('members')
