from database import get_db
from exceptions import JiraAgentError, NoOutputError
from fastapi import APIRouter, Depends
from jira import get_all_records, process_jira_request
from jira.schemas import JiraRequest, JiraRequestCreate, JiraResponse
from logger import log_error, logger
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/jira", tags=["Jira"])


@router.post("/agent", response_model=JiraResponse)
async def jira_agent(
    request: JiraRequestCreate, db: Session = Depends(get_db)
) -> JiraResponse:
    """Query the Jira agent"""
    try:
        logger.info(f"Processing Jira request: {request.request}")
        if output := await process_jira_request(db, request):
            logger.info("Successfully processed Jira request")
            return JiraResponse(output=output)
        raise NoOutputError()
    except Exception as e:
        log_error(logger, e, {"request": request.dict()})
        raise JiraAgentError(str(e)) from e


@router.get("/records", response_model=list[JiraRequest])
async def get_records(db: Session = Depends(get_db)) -> list[JiraRequest]:
    """Get all Jira request records"""
    try:
        logger.info("Fetching all Jira records")
        records = get_all_records(db)
        logger.info(f"Found {len(records)} records")
        return records
    except Exception as e:
        log_error(logger, e)
        raise JiraAgentError(str(e)) from e
