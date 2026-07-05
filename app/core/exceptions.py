"""Domain (business-rule) exceptions.

These are raised by the service layer and are intentionally free of any HTTP
knowledge. The API layer catches them and maps each to a status code + JSON
body. Keeping them here means services stay reusable outside a web request.
"""


class DomainError(Exception):
    """Base class for expected, client-facing errors.

    `message` is safe to show to the client -- it explains what went wrong in
    plain language, per the task's requirement that errors be informative.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class EmailAlreadyExistsError(DomainError):
    """A user with this email already exists. -> HTTP 409 Conflict."""


class UserNotFoundError(DomainError):
    """A referenced user does not exist. -> HTTP 404 / 400."""


class InvalidTimeRangeError(DomainError):
    """An event's startTime is not before its endTime. -> HTTP 400."""


class InvalidCredentialsError(DomainError):
    """Login failed: unknown email or wrong password. -> HTTP 401."""
