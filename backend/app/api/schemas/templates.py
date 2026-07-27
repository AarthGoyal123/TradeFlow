"""Template API schemas."""

from pydantic import BaseModel, ConfigDict


class TemplateSummaryResponse(BaseModel):
    """Public template summary returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    version: str
    description: str

