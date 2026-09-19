from pydantic import BaseModel


class SchoolResponse(BaseModel):
    id: int
    name: str
    short_name: str | None = None
    address: str | None = None
    region: str | None = None
    municipality: str | None = None

    class Config:
        from_attributes = True


class SchoolUpdateRequest(BaseModel):
    name: str
    short_name: str | None = None
    address: str | None = None
    region: str | None = None
    municipality: str | None = None