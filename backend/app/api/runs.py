from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app import models, schemas
from app.database import get_db
from app.services.runner import run_suite

router = APIRouter()


@router.get("/", response_model=list[schemas.TestRunOut])
def list_runs(db: Session = Depends(get_db)):
    return db.query(models.TestRun).order_by(models.TestRun.id.desc()).all()


@router.post("/", response_model=schemas.TestRunDetailOut)
def create_run(payload: schemas.TestRunCreate, db: Session = Depends(get_db)):
    suite = (
        db.query(models.TestSuite)
        .options(joinedload(models.TestSuite.test_cases), joinedload(models.TestSuite.policy))
        .filter(models.TestSuite.id == payload.suite_id)
        .first()
    )
    if not suite:
        raise HTTPException(status_code=404, detail="Suite not found")
    if not suite.test_cases:
        raise HTTPException(status_code=400, detail="Suite has no test cases to run")

    connector = db.get(models.Connector, payload.connector_id)
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")

    run = run_suite(db, suite, connector)
    return run


@router.get("/{run_id}", response_model=schemas.TestRunDetailOut)
def get_run(run_id: int, db: Session = Depends(get_db)):
    run = (
        db.query(models.TestRun)
        .options(joinedload(models.TestRun.results))
        .filter(models.TestRun.id == run_id)
        .first()
    )
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run
