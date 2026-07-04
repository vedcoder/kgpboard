"""Maps exceptions to HTTP responses.

This is the ONLY place that connects our HTTP-free domain errors to status
codes. Everything below the API layer stays framework-agnostic.
"""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    DomainError,
    EmailAlreadyExistsError,
    InvalidTimeRangeError,
    UserNotFoundError,
)

# Which domain error becomes which HTTP status.
_STATUS_BY_ERROR: dict[type[DomainError], int] = {
    EmailAlreadyExistsError: status.HTTP_409_CONFLICT,
    UserNotFoundError: status.HTTP_400_BAD_REQUEST,
    InvalidTimeRangeError: status.HTTP_400_BAD_REQUEST,
}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def handle_domain_error(_: Request, exc: DomainError) -> JSONResponse:
        # Starlette matches handlers by the exception's MRO, so this one catches
        # every DomainError subclass. Default to 400 for any we didn't map.
        code = _STATUS_BY_ERROR.get(type(exc), status.HTTP_400_BAD_REQUEST)
        return JSONResponse(status_code=code, content={"detail": exc.message})

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        _: Request, exc: RequestValidationError
    ) -> JSONResponse:
        # FastAPI's default for bad/missing fields is 422; the task asks for 400.
        # We also flatten Pydantic's error list into a readable field->message form.
        errors = [
            {
                "field": ".".join(
                    str(part) for part in err["loc"] if part != "body"
                ),
                "message": err["msg"],
            }
            for err in exc.errors()
        ]
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Validation failed.", "errors": errors},
        )
