"""crm permissions.

Revision ID: f4b8f4d6c2b1
Revises: c83462d83061
Create Date: 2026-06-01
"""

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel

from alembic import op

revision: str = "f4b8f4d6c2b1"
down_revision: str | None = "c83462d83061"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Apply schema changes."""

    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.drop_constraint("ck_user_role", type_="check")
        batch_op.create_check_constraint(
            "ck_user_role",
            "role IN ('ADMIN', 'SALES', 'MANAGER', 'TECH')",
        )

    op.create_table(
        "crm_user_permission_override",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "permission",
            sqlmodel.sql.sqltypes.AutoString(length=120),
            nullable=False,
        ),
        sa.Column(
            "effect",
            sa.Enum("GRANT", "DENY", name="crmuserpermissioneffect"),
            nullable=False,
        ),
        sa.Column("changed_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "effect IN ('GRANT', 'DENY')",
            name=op.f("ck_crm_user_permission_override_effect"),
        ),
        sa.ForeignKeyConstraint(
            ["changed_by"],
            ["user.id"],
            name=op.f("fk_crm_user_permission_override_changed_by_user"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
            name=op.f("fk_crm_user_permission_override_user_id_user"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_crm_user_permission_override")),
        sa.UniqueConstraint(
            "user_id",
            "permission",
            name="uq_crm_user_permission_override_user_permission",
        ),
    )
    with op.batch_alter_table(
        "crm_user_permission_override",
        schema=None,
    ) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_crm_user_permission_override_changed_by"),
            ["changed_by"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_crm_user_permission_override_permission"),
            ["permission"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_crm_user_permission_override_user_id"),
            ["user_id"],
            unique=False,
        )

    op.create_table(
        "lead_assignment",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("lead_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("assigned_by", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("assigned_at", sa.DateTime(), nullable=False),
        sa.Column("unassigned_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["assigned_by"], ["user.id"], name=op.f("fk_lead_assignment_assigned_by_user")
        ),
        sa.ForeignKeyConstraint(
            ["lead_id"], ["lead.id"], name=op.f("fk_lead_assignment_lead_id_lead")
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["user.id"], name=op.f("fk_lead_assignment_user_id_user")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_lead_assignment")),
    )
    with op.batch_alter_table("lead_assignment", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_lead_assignment_assigned_by"),
            ["assigned_by"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_lead_assignment_is_active"),
            ["is_active"],
            unique=False,
        )
        batch_op.create_index(batch_op.f("ix_lead_assignment_lead_id"), ["lead_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_lead_assignment_user_id"), ["user_id"], unique=False)
        batch_op.create_index(
            "ix_lead_assignment_user_active",
            ["user_id", "is_active", "assigned_at", "id"],
            unique=False,
        )
        batch_op.create_index(
            "uq_lead_assignment_one_active",
            ["lead_id"],
            unique=True,
            sqlite_where=sa.text("is_active = 1"),
            postgresql_where=sa.text("is_active = true"),
        )

    op.create_table(
        "proposal_assignment",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("proposal_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("assigned_by", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("assigned_at", sa.DateTime(), nullable=False),
        sa.Column("unassigned_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["assigned_by"],
            ["user.id"],
            name=op.f("fk_proposal_assignment_assigned_by_user"),
        ),
        sa.ForeignKeyConstraint(
            ["proposal_id"],
            ["proposal.id"],
            name=op.f("fk_proposal_assignment_proposal_id_proposal"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["user.id"], name=op.f("fk_proposal_assignment_user_id_user")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_proposal_assignment")),
    )
    with op.batch_alter_table("proposal_assignment", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_proposal_assignment_assigned_by"),
            ["assigned_by"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_proposal_assignment_is_active"),
            ["is_active"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_proposal_assignment_proposal_id"),
            ["proposal_id"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_proposal_assignment_user_id"), ["user_id"], unique=False
        )
        batch_op.create_index(
            "ix_proposal_assignment_user_active",
            ["user_id", "is_active", "assigned_at", "id"],
            unique=False,
        )
        batch_op.create_index(
            "uq_proposal_assignment_active_user",
            ["proposal_id", "user_id"],
            unique=True,
            sqlite_where=sa.text("is_active = 1"),
            postgresql_where=sa.text("is_active = true"),
        )


def downgrade() -> None:
    """Revert schema changes."""

    op.drop_table("proposal_assignment")
    op.drop_table("lead_assignment")
    op.drop_table("crm_user_permission_override")
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.drop_constraint("ck_user_role", type_="check")
        batch_op.create_check_constraint(
            "ck_user_role",
            "role IN ('ADMIN', 'SALES', 'MANAGER')",
        )
