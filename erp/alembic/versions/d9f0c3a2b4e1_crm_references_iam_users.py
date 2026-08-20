"""crm references iam users.

Revision ID: d9f0c3a2b4e1
Revises: b6c2d8f90a31
Create Date: 2026-06-01
"""

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel

from alembic import op

revision: str = "d9f0c3a2b4e1"
down_revision: str | None = "b6c2d8f90a31"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

IAM_ADMIN_PERMISSIONS = (
    "iam.permissions.manage",
    "iam.permissions.read",
    "iam.services.manage",
    "iam.services.read",
    "iam.users.create",
    "iam.users.deactivate",
    "iam.users.read",
    "iam.users.update",
)

USER_FK_REWRITES = {
    "promoter": (("fk_promoter_owner_id_user", "owner_id"),),
    "stage_transition": (("fk_stage_transition_transitioned_by_user", "transitioned_by"),),
    "contact": (("fk_contact_owner_id_user", "owner_id"),),
    "lead": (("fk_lead_owner_id_user", "owner_id"),),
    "lead_document": (("fk_lead_document_uploaded_by_user", "uploaded_by"),),
    "lead_electricity_bill": (("fk_lead_electricity_bill_uploaded_by_user", "uploaded_by"),),
    "lead_interaction": (("fk_lead_interaction_created_by_user", "created_by"),),
    "proposal": (("fk_proposal_created_by_user", "created_by"),),
    "technical_visit": (("fk_technical_visit_created_by_user", "created_by"),),
    "technical_visit_assignee": (("fk_technical_visit_assignee_user_id_user", "user_id"),),
    "technical_visit_attachment": (
        ("fk_technical_visit_attachment_uploaded_by_user", "uploaded_by"),
    ),
    "proposal_technical_visit": (("fk_proposal_technical_visit_linked_by_user", "linked_by"),),
    "proposal_document": (("fk_proposal_document_uploaded_by_user", "uploaded_by"),),
    "proposal_commercial_document": (
        ("fk_proposal_commercial_document_uploaded_by_user", "uploaded_by"),
    ),
    "crm_user_access": (
        ("fk_crm_user_access_changed_by_user", "changed_by"),
        ("fk_crm_user_access_user_id_user", "user_id"),
    ),
    "crm_user_permission_override": (
        ("fk_crm_user_permission_override_changed_by_user", "changed_by"),
        ("fk_crm_user_permission_override_user_id_user", "user_id"),
    ),
    "lead_assignment": (
        ("fk_lead_assignment_assigned_by_user", "assigned_by"),
        ("fk_lead_assignment_user_id_user", "user_id"),
    ),
    "proposal_assignment": (
        ("fk_proposal_assignment_assigned_by_user", "assigned_by"),
        ("fk_proposal_assignment_user_id_user", "user_id"),
    ),
}


def _iam_fk_name(old_name: str) -> str:
    return old_name.removesuffix("_user") + "_iam_user"


def _retarget_user_fks(*, target_table: str) -> None:
    for table_name, specs in USER_FK_REWRITES.items():
        with op.batch_alter_table(table_name, schema=None) as batch_op:
            for old_name, _column_name in specs:
                source_name = old_name if target_table == "iam_user" else _iam_fk_name(old_name)
                batch_op.drop_constraint(source_name, type_="foreignkey")
            for old_name, column_name in specs:
                base_name = _iam_fk_name(old_name) if target_table == "iam_user" else old_name
                batch_op.create_foreign_key(
                    base_name,
                    target_table,
                    [column_name],
                    ["id"],
                )


def upgrade() -> None:
    """Apply schema changes."""

    op.execute(
        sa.text(
            "INSERT INTO iam_user "
            "(id, email, full_name, hashed_password, is_active, created_at, updated_at) "
            "SELECT id, email, full_name, hashed_password, is_active, created_at, updated_at "
            'FROM "user" '
            'WHERE NOT EXISTS (SELECT 1 FROM iam_user WHERE iam_user.id = "user".id)'
        )
    )

    op.execute(
        sa.text(
            "INSERT INTO iam_service_access "
            "(user_id, service_key, is_active, granted_by, created_at, updated_at) "
            "SELECT user_id, 'crm', is_active, COALESCE(changed_by, user_id), "
            "created_at, updated_at "
            "FROM crm_user_access "
            "WHERE NOT EXISTS ("
            "SELECT 1 FROM iam_service_access "
            "WHERE iam_service_access.user_id = crm_user_access.user_id "
            "AND iam_service_access.service_key = 'crm'"
            ")"
        )
    )

    for permission in IAM_ADMIN_PERMISSIONS:
        op.execute(
            sa.text(
                "INSERT INTO iam_user_permission_override "
                "(user_id, permission, effect, changed_by, created_at, updated_at) "
                "SELECT user_id, :permission, 'GRANT', "
                "COALESCE(changed_by, user_id), created_at, updated_at "
                "FROM verp_user_permission_override "
                "WHERE permission = 'verp.permissions.manage' "
                "AND effect = 'GRANT' "
                "AND NOT EXISTS ("
                "SELECT 1 FROM iam_user_permission_override "
                "WHERE iam_user_permission_override.user_id = "
                "verp_user_permission_override.user_id "
                "AND iam_user_permission_override.permission = :permission"
                ")"
            ).bindparams(permission=permission)
        )

    _retarget_user_fks(target_table="iam_user")
    op.drop_table("verp_user_permission_override")
    op.drop_table("user")


def downgrade() -> None:
    """Revert schema changes."""

    op.create_table(
        "user",
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
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user")),
    )
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_user_email"), ["email"], unique=True)

    op.execute(
        sa.text(
            'INSERT INTO "user" '
            "(id, email, full_name, hashed_password, is_active, created_at, updated_at) "
            "SELECT id, email, full_name, hashed_password, is_active, created_at, updated_at "
            "FROM iam_user"
        )
    )

    _retarget_user_fks(target_table="user")

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
