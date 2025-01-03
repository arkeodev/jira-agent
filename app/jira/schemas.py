from datetime import datetime

from pydantic import BaseModel


class JiraRequestBase(BaseModel):
    request: str


class JiraRequestCreate(JiraRequestBase):
    pass


class JiraRequest(JiraRequestBase):
    id: int
    response: str
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class JiraResponse(BaseModel):
    output: str
