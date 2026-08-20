"""verp identity platform admin.

Revision ID: a91c8d0f5b2e
Revises: f4b8f4d6c2b1
Create Date: 2026-06-01
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "a91c8d0f5b2e"
down_revision: str | None = "f4b8f4d6c2b1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Apply schema changes."""

    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "is_platform_admin",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            )
        )

    op.execute(
        sa.text(
            'UPDATE "user" SET is_platform_admin = 1 '
            "WHERE role = 'ADMIN' "
            "AND id = (SELECT MIN(id) FROM \"user\" WHERE role = 'ADMIN')"
        )
    )


def downgrade() -> None:
    """Revert schema changes."""

    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.drop_column("is_platform_admin")
