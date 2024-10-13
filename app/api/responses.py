from typing import Any, Generic, TypeVar

from fastapi.responses import ORJSONResponse
from pydantic import BaseModel

ResultT = TypeVar("ResultT", bound=BaseModel)
ErrorT = TypeVar("ErrorT", bound=BaseModel)


class SuccessResponse(BaseModel, Generic[ResultT]):
    result: ResultT
    success: bool = True
    errors: list[Any] = []


class ErrorMessage(BaseModel):
    message: str | None


class ValidationError(BaseModel):
    type: str
    loc: list[str | int]
    message: str


class ErrorResponse(BaseModel, Generic[ErrorT]):
    success: bool = False
    errors: list[ErrorT] = []


class GeneralResponse(ORJSONResponse):
    media_type = "application/json"

    def render(self, content: Any) -> bytes:
        return super().render({"result": content, "errors": [], "success": True})
