from typing import Any

from fastapi import HTTPException, status


class JiraAgentException(HTTPException):
    """Base exception for Jira Agent API"""

    def __init__(
        self, status_code: int, detail: str, headers: dict[str, Any] | None = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class DatabaseError(JiraAgentException):
    """Raised when a database operation fails"""

    def __init__(self, operation: str, detail: str) -> None:
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database {operation} failed: {detail}",
        )


class JiraAgentError(JiraAgentException):
    """Raised when the Jira agent fails to process a request"""

    def __init__(self, detail: str) -> None:
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Jira agent error: {detail}",
        )


class NoOutputError(JiraAgentException):
    """Raised when the agent produces no output"""

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Agent produced no output",
        )
