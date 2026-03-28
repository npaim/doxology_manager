"""add template link to services

Revision ID: f6e7d8c9b0a1
Revises: f1a2b3c4d5e6
Create Date: 2026-03-27
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f6e7d8c9b0a1"
down_revision: Union[str, Sequence[str], None] = "f1a2b3c4d5e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    cols = {c["name"] for c in insp.get_columns("services")}
    idxs = {i["name"] for i in insp.get_indexes("services")}

    if "template_id" not in cols:
        with op.batch_alter_table("services") as batch:
            batch.add_column(sa.Column("template_id", sa.Integer(), nullable=True))
            batch.create_foreign_key("fk_services_template_id", "templates", ["template_id"], ["id"], ondelete="SET NULL")
            batch.create_index("ix_services_template_id", ["template_id"])
    else:
        if "ix_services_template_id" not in idxs:
            op.create_index("ix_services_template_id", "services", ["template_id"])
        try:
            fks = insp.get_foreign_keys("services")
            if not any(fk.get("name") == "fk_services_template_id" for fk in fks):
                op.create_foreign_key("fk_services_template_id", "services", "templates", ["template_id"], ["id"], ondelete="SET NULL")
        except NotImplementedError:
            pass


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    cols = {c["name"] for c in insp.get_columns("services")}
    idxs = {i["name"] for i in insp.get_indexes("services")}

    if "template_id" in cols:
        with op.batch_alter_table("services") as batch:
            if "ix_services_template_id" in idxs:
                batch.drop_index("ix_services_template_id")
            try:
                batch.drop_constraint("fk_services_template_id", type_="foreignkey")
            except Exception:
                pass
            batch.drop_column("template_id")
