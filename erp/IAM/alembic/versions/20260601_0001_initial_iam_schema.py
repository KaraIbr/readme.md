"""initial iam schema."""

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel

from alembic import op

revision: str = "20260601_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Apply schema changes."""

    op.create_table(
        "iam_user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "email",
            sqlmodel.sql.sqltypes.AutoString(length=255),
            nullable=False,
        ),
        sa.Column(
            "full_name",
            sqlmodel.sql.sqltypes.AutoString(length=255),
            nullable=True,
        ),
        sa.Column("hashed_password", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("iam_user", schema=None) as batch_op:
        batch_op.create_index("ix_iam_user_email", ["email"], unique=True)
        batch_op.create_index("ix_iam_user_is_active", ["is_active"], unique=False)

    op.create_table(
        "iam_user_permission_override",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "permission",
            sqlmodel.sql.sqltypes.AutoString(length=120),
            nullable=False,
        ),
        sa.Column(
            "effect",
            sa.Enum("GRANT", "DENY", name="iamuserpermissioneffect"),
            nullable=False,
        ),
        sa.Column("changed_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "effect IN ('GRANT', 'DENY')",
            name="ck_iam_user_permission_override_effect",
        ),
        sa.ForeignKeyConstraint(["changed_by"], ["iam_user.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["iam_user.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "permission",
            name="uq_iam_user_permission_override_user_permission",
        ),
    )
    with op.batch_alter_table("iam_user_permission_override", schema=None) as batch_op:
        batch_op.create_index(
            "ix_iam_user_permission_override_changed_by",
            ["changed_by"],
            unique=False,
        )
        batch_op.create_index(
            "ix_iam_user_permission_override_permission",
            ["permission"],
            unique=False,
        )
        batch_op.create_index(
            "ix_iam_user_permission_override_user_id",
            ["user_id"],
            unique=False,
        )

    op.create_table(
        "iam_service_access",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "service_key",
            sqlmodel.sql.sqltypes.AutoString(length=80),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("granted_by", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["granted_by"], ["iam_user.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["iam_user.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "service_key",
            name="uq_iam_service_access_user_service",
        ),
    )
    with op.batch_alter_table("iam_service_access", schema=None) as batch_op:
        batch_op.create_index(
            "ix_iam_service_access_granted_by",
            ["granted_by"],
            unique=False,
        )
        batch_op.create_index(
            "ix_iam_service_access_is_active",
            ["is_active"],
            unique=False,
        )
        batch_op.create_index(
            "ix_iam_service_access_service_key",
            ["service_key"],
            unique=False,
        )
        batch_op.create_index(
            "ix_iam_service_access_user_id",
            ["user_id"],
            unique=False,
        )


def downgrade() -> None:
    """Revert schema changes."""

    with op.batch_alter_table("iam_service_access", schema=None) as batch_op:
        batch_op.drop_index("ix_iam_service_access_user_id")
        batch_op.drop_index("ix_iam_service_access_service_key")
        batch_op.drop_index("ix_iam_service_access_is_active")
        batch_op.drop_index("ix_iam_service_access_granted_by")
    op.drop_table("iam_service_access")

    with op.batch_alter_table("iam_user_permission_override", schema=None) as batch_op:
        batch_op.drop_index("ix_iam_user_permission_override_user_id")
        batch_op.drop_index("ix_iam_user_permission_override_permission")
        batch_op.drop_index("ix_iam_user_permission_override_changed_by")
    op.drop_table("iam_user_permission_override")

    with op.batch_alter_table("iam_user", schema=None) as batch_op:
        batch_op.drop_index("ix_iam_user_is_active")
        batch_op.drop_index("ix_iam_user_email")
    op.drop_table("iam_user")
