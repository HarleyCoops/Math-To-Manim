from __future__ import annotations

from typing import Any

import pydantic
from pydantic import BaseModel


PYDANTIC_V2 = int(pydantic.VERSION.split(".", 1)[0]) >= 2

if PYDANTIC_V2:
    from pydantic import ConfigDict, Field, model_validator

    root_validator = None
else:
    from pydantic import Field, root_validator

    ConfigDict = None
    model_validator = None


class ArtifactModel(BaseModel):
    """Shared Pydantic base for pipeline artifacts."""

    if PYDANTIC_V2:
        model_config = ConfigDict(
            extra="forbid",
            populate_by_name=True,
            validate_assignment=True,
        )
    else:

        class Config:
            extra = "forbid"
            allow_population_by_field_name = True
            validate_assignment = True

        @classmethod
        def model_validate(cls, obj: Any) -> "ArtifactModel":
            return cls.parse_obj(obj)

        @classmethod
        def model_json_schema(cls, *args: Any, **kwargs: Any) -> dict:
            return cls.schema(*args, **kwargs)

        def model_dump(self, *args: Any, **kwargs: Any) -> dict:
            kwargs.pop("mode", None)
            return self.dict(*args, **kwargs)

        def model_dump_json(self, *args: Any, **kwargs: Any) -> str:
            kwargs.pop("mode", None)
            return self.json(*args, **kwargs)

        def model_copy(self, *args: Any, **kwargs: Any) -> "ArtifactModel":
            return self.copy(*args, **kwargs)

    def to_public_dict(self) -> dict[str, Any]:
        """Return a JSON-safe representation for CLI/API responses."""

        return self.model_dump(mode="json")
