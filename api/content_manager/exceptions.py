from typing import Any

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse

from content_manager.models import Error


class ConflictException(HTTPException):
    def __init__(self, detail: Any = None, headers: dict[str, str] | None = None):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail, headers=headers)


class NotFoundException(HTTPException):
    def __init__(self, detail: Any = None, headers: dict[str, str] | None = None):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail, headers=headers)


def handle_4xx_exception(request: Request, exc: HTTPException):
    model = Error(message=exc.detail, status_code=exc.status_code)
    return JSONResponse(content=model.model_dump(), status_code=model.status_code)
