from fastapi import Request, status
from fastapi.responses import JSONResponse


class AppError(Exception):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, detail: str) -> None:
        self.detail = detail


class ResourceNotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND


class BusinessRuleViolationError(AppError):
    status_code = status.HTTP_409_CONFLICT


class EngineerUnavailableError(AppError):
    status_code = status.HTTP_409_CONFLICT


async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

