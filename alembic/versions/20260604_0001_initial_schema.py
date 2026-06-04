"""initial schema

Revision ID: 20260604_0001
Revises:
Create Date: 2026-06-04
"""
from typing import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260604_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    project_status = sa.Enum("ACTIVE", "COMPLETED", "ON_HOLD", name="projectstatus")
    sprint_status = sa.Enum("PLANNED", "IN_PROGRESS", "DONE", name="sprintstatus")
    task_priority = sa.Enum("LOW", "MEDIUM", "HIGH", "CRITICAL", name="taskpriority")
    task_status = sa.Enum("TODO", "IN_PROGRESS", "REVIEW", "DONE", name="taskstatus")

    op.create_table(
        "clients",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("industry", sa.String(length=100), nullable=False),
        sa.Column("contact_email", sa.String(length=254), nullable=False),
        sa.Column("country", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_clients_id"), "clients", ["id"])
    op.create_index(op.f("ix_clients_name"), "clients", ["name"])
    op.create_index(op.f("ix_clients_contact_email"), "clients", ["contact_email"], unique=True)

    op.create_table(
        "engineers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("primary_stack", sa.String(length=80), nullable=False),
        sa.Column("experience_years", sa.Integer(), nullable=False),
        sa.Column("is_available", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_engineers_id"), "engineers", ["id"])
    op.create_index(op.f("ix_engineers_email"), "engineers", ["email"], unique=True)
    op.create_index(op.f("ix_engineers_primary_stack"), "engineers", ["primary_stack"])

    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", project_status, nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("client_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_projects_id"), "projects", ["id"])
    op.create_index(op.f("ix_projects_name"), "projects", ["name"])
    op.create_index(op.f("ix_projects_client_id"), "projects", ["client_id"])

    op.create_table(
        "sprints",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sprint_number", sa.Integer(), nullable=False),
        sa.Column("goal", sa.Text(), nullable=False),
        sa.Column("status", sprint_status, nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_sprints_id"), "sprints", ["id"])
    op.create_index(op.f("ix_sprints_project_id"), "sprints", ["project_id"])

    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("priority", task_priority, nullable=False),
        sa.Column("status", task_status, nullable=False),
        sa.Column("estimated_hours", sa.Float(), nullable=False),
        sa.Column("actual_hours", sa.Float(), nullable=False),
        sa.Column("sprint_id", sa.Integer(), nullable=False),
        sa.Column("engineer_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["engineer_id"], ["engineers.id"]),
        sa.ForeignKeyConstraint(["sprint_id"], ["sprints.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tasks_id"), "tasks", ["id"])
    op.create_index(op.f("ix_tasks_title"), "tasks", ["title"])
    op.create_index(op.f("ix_tasks_sprint_id"), "tasks", ["sprint_id"])
    op.create_index(op.f("ix_tasks_engineer_id"), "tasks", ["engineer_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_tasks_engineer_id"), table_name="tasks")
    op.drop_index(op.f("ix_tasks_sprint_id"), table_name="tasks")
    op.drop_index(op.f("ix_tasks_title"), table_name="tasks")
    op.drop_index(op.f("ix_tasks_id"), table_name="tasks")
    op.drop_table("tasks")
    op.drop_index(op.f("ix_sprints_project_id"), table_name="sprints")
    op.drop_index(op.f("ix_sprints_id"), table_name="sprints")
    op.drop_table("sprints")
    op.drop_index(op.f("ix_projects_client_id"), table_name="projects")
    op.drop_index(op.f("ix_projects_name"), table_name="projects")
    op.drop_index(op.f("ix_projects_id"), table_name="projects")
    op.drop_table("projects")
    op.drop_index(op.f("ix_engineers_primary_stack"), table_name="engineers")
    op.drop_index(op.f("ix_engineers_email"), table_name="engineers")
    op.drop_index(op.f("ix_engineers_id"), table_name="engineers")
    op.drop_table("engineers")
    op.drop_index(op.f("ix_clients_contact_email"), table_name="clients")
    op.drop_index(op.f("ix_clients_name"), table_name="clients")
    op.drop_index(op.f("ix_clients_id"), table_name="clients")
    op.drop_table("clients")

