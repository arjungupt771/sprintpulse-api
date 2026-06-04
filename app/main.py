from fastapi import FastAPI

from app.core.exceptions import (
    AppError,
    app_error_handler,
)
from app.routers import clients, engineers, projects, sprints, tasks


def create_app() -> FastAPI:
    app = FastAPI(
        title="Tekravio Sprint Tracker API",
        version="0.1.0",
        description="Async FastAPI backend for sprint, task, and workload tracking.",
    )
    app.add_exception_handler(AppError, app_error_handler)
    app.include_router(clients.router)
    app.include_router(projects.router)
    app.include_router(sprints.router)
    app.include_router(tasks.router)
    app.include_router(engineers.router)
    return app


app = create_app()

