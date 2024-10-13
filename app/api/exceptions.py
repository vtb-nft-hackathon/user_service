from typing import Any

from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import ORJSONResponse
from starlette.requests import Request
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

HTTP_NETWORK_CONNECT_TIMEOUT = 599


class ApiError(HTTPException):
    status_code: int = HTTP_400_BAD_REQUEST
    headers: dict[str, str] | None = None
    media_type: str = "application/json"

    def __init__(self, content: Any = None):
        if content is not None:
            self.detail = content


def handle_api_exception(_: Request, exc: ApiError) -> ORJSONResponse:
    return ORJSONResponse(
        content={
            "success": False,
            "errors": (
                {
                    "message": exc.detail,
                },
            ),
        },
        headers=exc.headers,
        media_type=exc.media_type,
        status_code=exc.status_code,
    )


def handle_validation_exception(_: Request, exc: RequestValidationError) -> ORJSONResponse:
    def rename_message_key(err: dict[str, str]) -> dict[str, str]:
        err["message"] = err.pop("msg")
        return err

    return ORJSONResponse(
        content={
            "success": False,
            "errors": tuple(rename_message_key(err) for err in exc.errors()),
        },
        media_type="application/json",
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
    )


def handle_500_exception(_: Request, __: Exception) -> ORJSONResponse:
    return ORJSONResponse(
        content={
            "success": False,
            "errors": [
                {
                    "message": "Internal Server Error",
                },
            ],
        },
        media_type="application/json",
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
    )


def handle_404_exception(_: Request, exc: ApiError) -> ORJSONResponse:
    return ORJSONResponse(
        content={
            "success": False,
            "errors": [
                {
                    "message": exc.detail,
                }
            ],
        },
        media_type="application/json",
        status_code=HTTP_404_NOT_FOUND,
    )


class ForbiddenError(ApiError):
    status_code: int = HTTP_403_FORBIDDEN
    detail: str = "Forbidden"


class NotFoundError(ApiError):
    status_code: int = HTTP_404_NOT_FOUND
    detail: str = "Not found"


class ConflictError(ApiError):
    status_code: int = HTTP_409_CONFLICT
    detail: str = "Conflict"


class NetworkConnectError(ApiError):
    status_code: int = HTTP_NETWORK_CONNECT_TIMEOUT
    detail: str = "Network connect timeout"
