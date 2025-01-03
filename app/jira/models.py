from database import Base
from sqlalchemy import Column, DateTime, Integer, Text
from sqlalchemy.sql import func


class JiraRequest(Base):
    __tablename__ = "jira_requests"

    id = Column(Integer, primary_key=True, index=True)
    request = Column(Text)
    response = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
