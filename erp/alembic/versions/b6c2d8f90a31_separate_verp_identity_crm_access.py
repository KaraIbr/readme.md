"""separate verp identity from crm access.

Revision ID: b6c2d8f90a31
Revises: a91c8d0f5b2e
Create Date: 2026-06-01
"""

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel

from alembic import op

revision: str = "b6c2d8f90a31"
down_revision: str | None = "a91c8d0f5b2e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

VERP_BOOTSTRAP_PERMISSIONS = (
    "verp.permissions.manage",
    "verp.permissions.read",
    "verp.users.create",
)


def upgrade() -> None:
    """Apply schema changes."""

    op.create_table(
        "crm_user_access",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "role",
            sa.Enum("ADMIN", "SALES", "MANAGER", "TECH", name="crmuserrole"),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("changed_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "role IN ('ADMIN', 'SALES', 'MANAGER', 'TECH')",
            name=op.f("ck_crm_user_access_role"),
        ),
        sa.ForeignKeyConstraint(
            ["changed_by"],
            ["user.id"],
            name=op.f("fk_crm_user_access_changed_by_user"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
            name=op.f("fk_crm_user_access_user_id_user"),
        ),
        sa.PrimaryKeyConstraint("user_id", name=op.f("pk_crm_user_access")),
    )
    with op.batch_alter_table("crm_user_access", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_crm_user_access_changed_by"),
            ["changed_by"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_crm_user_access_is_active"),
            ["is_active"],
            unique=False,
        )

    op.create_table(
        "verp_user_permission_override",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "permission",
            sqlmodel.sql.sqltypes.AutoString(length=120),
            nullable=False,
        ),
        sa.Column(
            "effect",
            sa.Enum("GRANT", "DENY", name="verpuserpermissioneffect"),
            nullable=False,
        ),
        sa.Column("changed_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "effect IN ('GRANT', 'DENY')",
            name=op.f("ck_verp_user_permission_override_effect"),
        ),
        sa.ForeignKeyConstraint(
            ["changed_by"],
            ["user.id"],
            name=op.f("fk_verp_user_permission_override_changed_by_user"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
            name=op.f("fk_verp_user_permission_override_user_id_user"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_verp_user_permission_override")),
        sa.UniqueConstraint(
            "user_id",
            "permission",
            name="uq_verp_user_permission_override_user_permission",
        ),
    )
    with op.batch_alter_table(
        "verp_user_permission_override",
        schema=None,
    ) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_verp_user_permission_override_changed_by"),
            ["changed_by"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_verp_user_permission_override_permission"),
            ["permission"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_verp_user_permission_override_user_id"),
            ["user_id"],
            unique=False,
        )

    op.execute(
        sa.text(
            "INSERT INTO crm_user_access "
            "(user_id, role, is_active, changed_by, created_at, updated_at) "
            'SELECT id, role, is_active, NULL, created_at, updated_at FROM "user"'
        )
    )
    for permission in VERP_BOOTSTRAP_PERMISSIONS:
        op.execute(
            sa.text(
                "INSERT INTO verp_user_permission_override "
                "(user_id, permission, effect, changed_by, created_at, updated_at) "
                "SELECT id, :permission, 'GRANT', id, created_at, updated_at "
                'FROM "user" WHERE is_platform_admin = 1'
            ).bindparams(permission=permission)
        )

    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.drop_constraint("ck_user_role", type_="check")
        batch_op.drop_column("role")
        batch_op.drop_column("is_platform_admin")


def downgrade() -> None:
    """Revert schema changes."""

    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "role",
                sa.Enum("ADMIN", "SALES", "MANAGER", "TECH", name="userrole"),
                nullable=False,
                server_default="SALES",
            )
        )
        batch_op.add_column(
            sa.Column(
                "is_platform_admin",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            )
        )
        batch_op.create_check_constraint(
            "ck_user_role",
            "role IN ('ADMIN', 'SALES', 'MANAGER', 'TECH')",
        )

    op.execute(
        sa.text(
            'UPDATE "user" SET role = ('
            "SELECT crm_user_access.role FROM crm_user_access "
            'WHERE crm_user_access.user_id = "user".id'
            ") WHERE EXISTS ("
            "SELECT 1 FROM crm_user_access "
            'WHERE crm_user_access.user_id = "user".id'
            ")"
        )
    )
    op.execute(
        sa.text(
            'UPDATE "user" SET is_platform_admin = 1 WHERE id IN ('
            "SELECT user_id FROM verp_user_permission_override "
            "WHERE permission = 'verp.users.create' AND effect = 'GRANT'"
            ")"
        )
    )

    op.drop_table("verp_user_permission_override")
    op.drop_table("crm_user_access")
