from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app import models, schemas
from app.database import get_db

router = APIRouter()


@router.get("/", response_model=list[schemas.TestSuiteOut])
def list_suites(db: Session = Depends(get_db)):
    return (
        db.query(models.TestSuite)
        .options(joinedload(models.TestSuite.test_cases))
        .order_by(models.TestSuite.id.desc())
        .all()
    )


@router.post("/", response_model=schemas.TestSuiteOut)
def create_suite(payload: schemas.TestSuiteCreate, db: Session = Depends(get_db)):
    suite = models.TestSuite(**payload.model_dump())
    db.add(suite)
    db.commit()
    db.refresh(suite)
    return suite


@router.get("/{suite_id}", response_model=schemas.TestSuiteOut)
def get_suite(suite_id: int, db: Session = Depends(get_db)):
    suite = db.get(models.TestSuite, suite_id)
    if not suite:
        raise HTTPException(status_code=404, detail="Suite not found")
    return suite


@router.delete("/{suite_id}")
def delete_suite(suite_id: int, db: Session = Depends(get_db)):
    suite = db.get(models.TestSuite, suite_id)
    if not suite:
        raise HTTPException(status_code=404, detail="Suite not found")
    db.delete(suite)
    db.commit()
    return {"status": "deleted"}
