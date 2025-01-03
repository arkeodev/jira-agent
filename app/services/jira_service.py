from logger import logger
from models import JiraRequest
from schemas import JiraRequest as JiraRequestSchema
from schemas import JiraRequestCreate
from sqlalchemy.orm import Session
from utils.model_utils import agent


async def process_jira_request(db: Session, request: JiraRequestCreate) -> str | None:
    """Process a Jira request through the agent and store the result"""
    try:
        # Call the agent
        response = agent.invoke({"input": request.request})
        if output := response.get("output"):
            # Save request and response
            db_request = JiraRequest(request=request.request, response=output)
            db.add(db_request)
            db.commit()
            db.refresh(db_request)
            return str(output)
        return None
    except Exception as e:
        logger.error(f"Error processing Jira request: {e}")
        raise


def get_all_records(db: Session) -> list[JiraRequestSchema]:
    """Get all Jira request records"""
    return [
        JiraRequestSchema.model_validate(record)
        for record in db.query(JiraRequest).all()
    ]
