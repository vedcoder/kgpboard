"""Shared Pydantic base for all API schemas."""

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    """Base schema: snake_case in Python, camelCase on the wire.

    - `alias_generator=to_camel`  -> `created_at` is exposed as `createdAt`.
    - `populate_by_name=True`     -> requests may use either name or alias.
    - `from_attributes=True`      -> can build a response straight from an ORM
                                     object (e.g. `UserRead.model_validate(user)`),
                                     which is what FastAPI does with response_model.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )
