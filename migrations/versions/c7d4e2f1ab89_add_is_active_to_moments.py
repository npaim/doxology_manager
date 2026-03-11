"""add is_active column to moments

Revision ID: c7d4e2f1ab89
Revises: a5c3e1d2f9ab
Create Date: 2026-03-11
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'c7d4e2f1ab89'
down_revision: Union[str, Sequence[str], None] = 'a5c3e1d2f9ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    cols = {c['name'] for c in insp.get_columns('moments')}
    if 'is_active' not in cols:
        op.add_column('moments', sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')))


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    cols = {c['name'] for c in insp.get_columns('moments')}
    if 'is_active' in cols:
        with op.batch_alter_table('moments', recreate='always') as batch:
            batch.drop_column('is_active')