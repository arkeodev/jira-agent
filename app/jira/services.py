from jira.models import JiraRequest
from jira.schemas import JiraRequest as JiraRequestSchema
from jira.schemas import JiraRequestCreate
from logger import logger
from sqlalchemy.orm import Session
from utils.model_utils import agent_executor


async def process_jira_request(db: Session, request: JiraRequestCreate) -> str | None:
    """Process a Jira request through the agent and store the result"""
    try:
        logger.debug(f"Processing Jira request: {request.request}")
        # Call the agent
        response = agent_executor.invoke({"input": request.request})
        logger.debug(f"Agent response: {response}")

        if output := response.get("output"):
            logger.debug(f"Agent output: {output}")
            # Save request and response
            db_request = JiraRequest(request=request.request, response=output)
            db.add(db_request)
            db.commit()
            db.refresh(db_request)
            logger.info(f"Successfully saved Jira request with ID: {db_request.id}")
            return str(output)

        logger.warning("No output from agent")
        return None
    except Exception as e:
        logger.error(f"Error processing Jira request: {e}", exc_info=True)
        raise


def get_all_records(db: Session) -> list[JiraRequestSchema]:
    """Get all Jira request records"""
    try:
        logger.debug("Fetching all Jira request records")
        records = [
            JiraRequestSchema.model_validate(record)
            for record in db.query(JiraRequest).all()
        ]
        logger.debug(f"Found {len(records)} records")
        return records
    except Exception as e:
        logger.error(f"Error fetching Jira records: {e}", exc_info=True)
        raise
