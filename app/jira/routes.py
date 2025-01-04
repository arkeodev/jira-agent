"""Routes for Jira-related endpoints."""
from database import get_db
from exceptions import JiraAgentError, NoOutputError
from fastapi import APIRouter, Depends
from jira.schemas import JiraRequest, JiraRequestCreate, JiraResponse
from jira.services import get_jira_service
from logger import log_error, logger
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/jira", tags=["Jira"])


@router.get("/projects")
async def get_projects(
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """Get all available Jira projects.

    Args:
        db: Database session

    Returns:
        Dictionary mapping project keys to project names

    Raises:
        JiraAgentError: If fetching projects fails
    """
    try:
        logger.info("Fetching all Jira projects")
        service = get_jira_service(db)
        projects = await service.get_projects()
        logger.info(f"Found {len(projects)} projects")
        return projects
    except Exception as e:
        log_error(logger, e)
        raise JiraAgentError(str(e)) from e


@router.post("/agent", response_model=JiraResponse)
async def jira_agent(
    request: JiraRequestCreate,
    db: Session = Depends(get_db),
) -> JiraResponse:
    """Query the Jira agent.

    Args:
        request: The Jira request to process
        db: Database session

    Returns:
        The agent's response

    Raises:
        JiraAgentError: If processing fails
        NoOutputError: If no output is produced
    """
    try:
        logger.info(f"Processing Jira request: {request.request}")
        service = get_jira_service(db)
        if output := await service.process_request(request):
            logger.info("Successfully processed Jira request")
            return JiraResponse(output=output)
        raise NoOutputError()
    except Exception as e:
        log_error(logger, e, {"request": request.dict()})
        raise JiraAgentError(str(e)) from e


@router.get("/records", response_model=list[JiraRequest])
async def get_records(
    db: Session = Depends(get_db),
) -> list[JiraRequest]:
    """Get all Jira request records.

    Args:
        db: Database session

    Returns:
        List of all Jira request records

    Raises:
        JiraAgentError: If fetching records fails
    """
    try:
        logger.info("Fetching all Jira records")
        service = get_jira_service(db)
        records = service.get_all_records()
        logger.info(f"Found {len(records)} records")
        return records
    except Exception as e:
        log_error(logger, e)
        raise JiraAgentError(str(e)) from e
