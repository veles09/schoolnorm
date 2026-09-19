from pydantic import BaseModel


class SchoolDocumentResponse(BaseModel):
    id: int
    document_type: str
    title: str
    number: str | None
    status: str

    class Config:
        from_attributes = True