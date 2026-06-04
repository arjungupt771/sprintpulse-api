from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import ProjectStatus, SprintStatus, TaskPriority, TaskStatus


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    industry: Mapped[str] = mapped_column(String(100), nullable=False)
    contact_email: Mapped[str] = mapped_column(String(254), nullable=False, unique=True, index=True)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    projects: Mapped[list["Project"]] = relationship(
        back_populates="client", cascade="all, delete-orphan", lazy="selectin"
    )


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[ProjectStatus] = mapped_column(Enum(ProjectStatus), default=ProjectStatus.ACTIVE)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False, index=True)

    client: Mapped[Client] = relationship(back_populates="projects")
    sprints: Mapped[list["Sprint"]] = relationship(
        back_populates="project", cascade="all, delete-orphan", lazy="selectin"
    )


class Sprint(Base):
    __tablename__ = "sprints"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    sprint_number: Mapped[int] = mapped_column(Integer, nullable=False)
    goal: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[SprintStatus] = mapped_column(Enum(SprintStatus), default=SprintStatus.PLANNED)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)

    project: Mapped[Project] = relationship(back_populates="sprints")
    tasks: Mapped[list["Task"]] = relationship(
        back_populates="sprint", cascade="all, delete-orphan", lazy="selectin"
    )


class Engineer(Base):
    __tablename__ = "engineers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(254), nullable=False, unique=True, index=True)
    primary_stack: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    experience_years: Mapped[int] = mapped_column(Integer, nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    tasks: Mapped[list["Task"]] = relationship(back_populates="engineer", lazy="selectin")


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[TaskPriority] = mapped_column(Enum(TaskPriority), default=TaskPriority.MEDIUM)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), default=TaskStatus.TODO)
    estimated_hours: Mapped[float] = mapped_column(Float, nullable=False)
    actual_hours: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    sprint_id: Mapped[int] = mapped_column(ForeignKey("sprints.id"), nullable=False, index=True)
    engineer_id: Mapped[int | None] = mapped_column(ForeignKey("engineers.id"), nullable=True, index=True)

    sprint: Mapped[Sprint] = relationship(back_populates="tasks")
    engineer: Mapped[Engineer | None] = relationship(back_populates="tasks")

