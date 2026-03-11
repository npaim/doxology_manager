"""add moments table and link from service_moments

Revision ID: f00dbabe42a1
Revises: baddcafe1234
Create Date: 2026-03-11
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'f00dbabe42a1'
down_revision: Union[str, Sequence[str], None] = 'baddcafe1234'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def _has_table(insp, name: str) -> bool:
    try:
        return insp.has_table(name)
    except Exception:
        return name in insp.get_table_names()


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    # templates catalog (idempotent)
    if not _has_table(insp, 'templates'):
        op.create_table(
            'templates',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('name', sa.String(), nullable=False),
            sa.UniqueConstraint('name', name='uq_templates_name'),
        )

    # moments table
    if not _has_table(insp, 'moments'):
        op.create_table(
            'moments',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('template_id', sa.Integer(), sa.ForeignKey('templates.id', ondelete='RESTRICT'), nullable=True),
            sa.Column('default_moment', sa.Boolean(), nullable=False, server_default=sa.text('false')),
            sa.Column('duration_min', sa.Integer(), nullable=True),
            sa.UniqueConstraint('name', name='uq_moments_name'),
        )
        op.create_index('ix_moments_template_id', 'moments', ['template_id'])
    else:
        cols = {c['name'] for c in insp.get_columns('moments')}
        if 'template_id' not in cols:
            op.add_column('moments', sa.Column('template_id', sa.Integer(), nullable=True))
        if 'default_moment' not in cols:
            op.add_column('moments', sa.Column('default_moment', sa.Boolean(), nullable=False, server_default=sa.text('false')))
        if 'duration_min' not in cols:
            op.add_column('moments', sa.Column('duration_min', sa.Integer(), nullable=True))
        idxs = {i['name'] for i in insp.get_indexes('moments')}
        if 'ix_moments_template_id' not in idxs and 'template_id' in cols:
            op.create_index('ix_moments_template_id', 'moments', ['template_id'])
        try:
            fks = insp.get_foreign_keys('moments')
            if not any(fk.get('name') == 'fk_moments_template' for fk in fks):
                op.create_foreign_key('fk_moments_template', 'moments', 'templates', ['template_id'], ['id'], ondelete='RESTRICT')
        except NotImplementedError:
            pass

    # service_moments link to moments
    if _has_table(insp, 'service_moments'):
        cols_sm = {c['name'] for c in insp.get_columns('service_moments')}
        if 'moment_id' not in cols_sm:
            try:
                with op.batch_alter_table('service_moments', recreate='always') as batch:
                    batch.add_column(sa.Column('moment_id', sa.Integer(), nullable=True))
                    batch.create_foreign_key('fk_service_moments_moment', 'moments', ['moment_id'], ['id'], ondelete='RESTRICT')
                    batch.create_index('ix_service_moments_moment_id', ['moment_id'])
            except NotImplementedError:
                op.add_column('service_moments', sa.Column('moment_id', sa.Integer(), nullable=True))
                idxs_sm = {i['name'] for i in insp.get_indexes('service_moments')}
                if 'ix_service_moments_moment_id' not in idxs_sm:
                    op.create_index('ix_service_moments_moment_id', 'service_moments', ['moment_id'])
        else:
            idxs_sm = {i['name'] for i in insp.get_indexes('service_moments')}
            if 'ix_service_moments_moment_id' not in idxs_sm:
                try:
                    op.create_index('ix_service_moments_moment_id', 'service_moments', ['moment_id'])
                except Exception:
                    pass
            try:
                fks_sm = insp.get_foreign_keys('service_moments')
                if not any(fk.get('name') == 'fk_service_moments_moment' for fk in fks_sm):
                    op.create_foreign_key('fk_service_moments_moment', 'service_moments', 'moments', ['moment_id'], ['id'], ondelete='RESTRICT')
            except NotImplementedError:
                pass


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    if _has_table(insp, 'service_moments'):
        try:
            with op.batch_alter_table('service_moments', recreate='always') as batch:
                idxs_sm = {i['name'] for i in insp.get_indexes('service_moments')}
                if 'ix_service_moments_moment_id' in idxs_sm:
                    batch.drop_index('ix_service_moments_moment_id')
                try:
                    batch.drop_constraint('fk_service_moments_moment', type_='foreignkey')
                except Exception:
                    pass
                cols_sm = {c['name'] for c in insp.get_columns('service_moments')}
                if 'moment_id' in cols_sm:
                    batch.drop_column('moment_id')
        except NotImplementedError:
            pass

    try:
        op.drop_index('ix_moments_template_id', table_name='moments')
    except Exception:
        pass
    if _has_table(insp, 'moments'):
        op.drop_table('moments')
    if _has_table(insp, 'templates'):
        op.drop_table('templates')