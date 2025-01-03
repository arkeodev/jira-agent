from database import get_db
from exceptions import DatabaseError
from fastapi import APIRouter, Depends
from logger import log_error, logger
from schemas import TestItem, TestItemCreate
from services import test_service
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/test", tags=["Test"])


@router.post("/item", response_model=TestItem)
async def create_test_item(
    item: TestItemCreate, db: Session = Depends(get_db)
) -> TestItem:
    """Create a new test item"""
    try:
        logger.info(f"Creating test item: {item.name}")
        result = test_service.create_test_item(db, item)
        logger.info(f"Successfully created test item with id: {result.id}")
        return result
    except Exception as e:
        log_error(logger, e, {"item": item.dict()})
        raise DatabaseError("create", str(e)) from e


@router.get("/items", response_model=list[TestItem])
async def get_test_items(db: Session = Depends(get_db)) -> list[TestItem]:
    """Get all test items"""
    try:
        logger.info("Fetching all test items")
        items = test_service.get_test_items(db)
        logger.info(f"Found {len(items)} items")
        return items
    except Exception as e:
        log_error(logger, e)
        raise DatabaseError("read", str(e)) from e
