from datetime import datetime

from pydantic import BaseModel


class TestItemBase(BaseModel):
    name: str


class TestItemCreate(TestItemBase):
    pass


class TestItem(TestItemBase):
    id: int
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


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


class HealthResponse(BaseModel):
    message: str
