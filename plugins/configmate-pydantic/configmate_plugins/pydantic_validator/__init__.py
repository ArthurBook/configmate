""" Pydantic Validator Plugin
extends the configmate library with a validator that uses pydantic to validate input
"""

from configmate_plugins.pydantic_validator.pydantic_validator import (
    PydanticValidator,
    validate_with_pydantic,
)

__all__ = ["PydanticValidator", "validate_with_pydantic"]
