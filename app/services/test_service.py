from models import TestModel
from schemas import TestItem, TestItemCreate
from sqlalchemy.orm import Session


def create_test_item(db: Session, item: TestItemCreate) -> TestItem:
    """Create a new test item"""
    db_item = TestModel(name=item.name)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    result: TestItem = TestItem.model_validate(db_item)
    return result


def get_test_items(db: Session) -> list[TestItem]:
    """Get all test items"""
    db_items = db.query(TestModel).all()
    return [TestItem.model_validate(item) for item in db_items]
