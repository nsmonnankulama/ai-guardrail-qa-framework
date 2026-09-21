from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.guardrails.registry import CATEGORIES
from app.services.generator import generate_test_prompts

router = APIRouter()


@router.get("/categories")
def list_categories():
    return CATEGORIES


@router.get("/", response_model=list[schemas.TestCaseOut])
def list_test_cases(suite_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(models.TestCase)
    if suite_id is not None:
        query = query.filter(models.TestCase.suite_id == suite_id)
    return query.order_by(models.TestCase.id.desc()).all()


@router.post("/", response_model=schemas.TestCaseOut)
def create_test_case(payload: schemas.TestCaseCreate, db: Session = Depends(get_db)):
    if payload.category not in CATEGORIES:
        raise HTTPException(status_code=400, detail=f"category must be one of {CATEGORIES}")
    suite = db.get(models.TestSuite, payload.suite_id)
    if not suite:
        raise HTTPException(status_code=404, detail="Suite not found")
    case = models.TestCase(**payload.model_dump())
    db.add(case)
    db.commit()
    db.refresh(case)
    return case


@router.delete("/{case_id}")
def delete_test_case(case_id: int, db: Session = Depends(get_db)):
    case = db.get(models.TestCase, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Test case not found")
    db.delete(case)
    db.commit()
    return {"status": "deleted"}


@router.post("/generate", response_model=list[schemas.TestCaseOut])
def generate_cases(payload: schemas.TestCaseGenerateRequest, db: Session = Depends(get_db)):
    if payload.category not in CATEGORIES:
        raise HTTPException(status_code=400, detail=f"category must be one of {CATEGORIES}")
    suite = db.get(models.TestSuite, payload.suite_id)
    if not suite:
        raise HTTPException(status_code=404, detail="Suite not found")

    try:
        prompts = generate_test_prompts(
            category=payload.category,
            company_name=payload.company_name,
            product_name=payload.product_name,
            allowed_topics=payload.allowed_topics,
            competitor_names=payload.competitor_names,
            count=payload.count,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI generation failed: {exc}")

    default_expected = "refuse" if payload.category in (
        "prompt_injection",
        "pii_leakage",
        "toxicity_harmful_content",
        "refusal_correctness",
    ) else "comply"

    created = []
    for prompt in prompts:
        case = models.TestCase(
            suite_id=suite.id,
            category=payload.category,
            prompt=prompt,
            expected_behavior=default_expected,
        )
        db.add(case)
        created.append(case)

    db.commit()
    for case in created:
        db.refresh(case)
    return created
