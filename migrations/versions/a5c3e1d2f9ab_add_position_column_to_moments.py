"""add position column to moments

Revision ID: a5c3e1d2f9ab
Revises: f00dbabe42a1
Create Date: 2026-03-11
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a5c3e1d2f9ab'
down_revision: Union[str, Sequence[str], None] = 'f00dbabe42a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    # add column if missing
    cols = {c['name'] for c in insp.get_columns('moments')}
    if 'position' not in cols:
        op.add_column('moments', sa.Column('position', sa.Integer(), nullable=True))
    # index optional for ordering; create if not present
    try:
        idxs = {i['name'] for i in insp.get_indexes('moments')}
        if 'ix_moments_position' not in idxs:
            op.create_index('ix_moments_position', 'moments', ['position'])
    except Exception:
        pass


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    try:
        op.drop_index('ix_moments_position', table_name='moments')
    except Exception:
        pass
    cols = {c['name'] for c in insp.get_columns('moments')}
    if 'position' in cols:
        with op.batch_alter_table('moments', recreate='always') as batch:
            batch.drop_column('position')