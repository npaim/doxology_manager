"""add churches, leaders, leader roles, and service ownership

Revision ID: f1a2b3c4d5e6
Revises: c7d4e2f1ab89
Create Date: 2026-03-25
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f1a2b3c4d5e6"
down_revision: Union[str, Sequence[str], None] = "c7d4e2f1ab89"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "churches",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    )

    op.create_table(
        "leaders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("church_id", sa.Integer(), sa.ForeignKey("churches.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=False, server_default="admin"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    )
    op.create_index("ix_leaders_church_id", "leaders", ["church_id"])
    op.create_index("ix_leaders_email", "leaders", ["email"], unique=True)

    churches = sa.table("churches", sa.column("id", sa.Integer()), sa.column("name", sa.String()))
    op.bulk_insert(churches, [{"id": 1, "name": "Default Church"}])

    with op.batch_alter_table("services") as batch:
        batch.add_column(sa.Column("church_id", sa.Integer(), nullable=True))
    op.execute(sa.text("UPDATE services SET church_id = 1 WHERE church_id IS NULL"))
    with op.batch_alter_table("services") as batch:
        batch.alter_column("church_id", nullable=False)
        batch.create_foreign_key("fk_services_church_id", "churches", ["church_id"], ["id"], ondelete="CASCADE")
        batch.create_index("ix_services_church_id", ["church_id"])


def downgrade() -> None:
    with op.batch_alter_table("services") as batch:
        batch.drop_index("ix_services_church_id")
        batch.drop_constraint("fk_services_church_id", type_="foreignkey")
        batch.drop_column("church_id")

    op.drop_index("ix_leaders_email", table_name="leaders")
    op.drop_index("ix_leaders_church_id", table_name="leaders")
    op.drop_table("leaders")
    op.drop_table("churches")
