"""Service layer for Jira request processing."""
from functools import lru_cache
from typing import Any, Optional

from agent import create_jira_agent
from agent.core.callbacks import AgentCallbackHandler
from jira.models import JiraRequest
from jira.schemas import JiraRequest as JiraRequestSchema
from jira.schemas import JiraRequestCreate
from logger import logger
from sqlalchemy.orm import Session


@lru_cache()
def get_jira_agent() -> Any:
    """Get or create a Jira agent instance.

    Returns:
        Configured JiraAgent instance
    """
    return create_jira_agent(callbacks=[AgentCallbackHandler()])


class JiraService:
    """Service for handling Jira-related operations."""

    def __init__(self, db: Session):
        """Initialize the Jira service.

        Args:
            db: Database session
        """
        self.db = db
        self.agent = get_jira_agent()

    async def process_request(self, request: JiraRequestCreate) -> Optional[str]:
        """Process a Jira request through the agent and store the result.

        Args:
            request: The Jira request to process

        Returns:
            The agent's response or None if no output

        Raises:
            Exception: If processing fails
        """
        try:
            logger.debug(f"Processing Jira request: {request.request}")

            # Call the agent
            response = await self.agent.execute({"input": request.request})
            logger.debug(f"Agent response: {response}")

            if output := response.get("output"):
                logger.debug(f"Agent output: {output}")

                # Save request and response
                db_request = JiraRequest(request=request.request, response=output)
                self.db.add(db_request)
                self.db.commit()
                self.db.refresh(db_request)
                logger.info(f"Successfully saved Jira request with ID: {db_request.id}")
                return str(output)

            logger.warning("No output from agent")
            return None

        except Exception as e:
            logger.error(f"Error processing Jira request: {e}", exc_info=True)
            raise

    def get_all_records(self) -> list[JiraRequestSchema]:
        """Get all Jira request records.

        Returns:
            List of all Jira request records

        Raises:
            Exception: If fetching records fails
        """
        try:
            logger.debug("Fetching all Jira request records")
            records = [
                JiraRequestSchema.model_validate(record)
                for record in self.db.query(JiraRequest).all()
            ]
            logger.debug(f"Found {len(records)} records")
            return records
        except Exception as e:
            logger.error(f"Error fetching Jira records: {e}", exc_info=True)
            raise


# Factory function for service creation
def get_jira_service(db: Session) -> JiraService:
    """Create a Jira service instance.

    Args:
        db: Database session

    Returns:
        Configured JiraService instance
    """
    return JiraService(db)
