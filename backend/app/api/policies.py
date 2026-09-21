from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter()


@router.get("/", response_model=list[schemas.GuardrailPolicyOut])
def list_policies(db: Session = Depends(get_db)):
    return db.query(models.GuardrailPolicy).order_by(models.GuardrailPolicy.id.desc()).all()


@router.post("/", response_model=schemas.GuardrailPolicyOut)
def create_policy(payload: schemas.GuardrailPolicyCreate, db: Session = Depends(get_db)):
    policy = models.GuardrailPolicy(**payload.model_dump())
    db.add(policy)
    db.commit()
    db.refresh(policy)
    return policy


@router.get("/{policy_id}", response_model=schemas.GuardrailPolicyOut)
def get_policy(policy_id: int, db: Session = Depends(get_db)):
    policy = db.get(models.GuardrailPolicy, policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy


@router.put("/{policy_id}", response_model=schemas.GuardrailPolicyOut)
def update_policy(policy_id: int, payload: schemas.GuardrailPolicyCreate, db: Session = Depends(get_db)):
    policy = db.get(models.GuardrailPolicy, policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    for field, value in payload.model_dump().items():
        setattr(policy, field, value)
    db.commit()
    db.refresh(policy)
    return policy


@router.delete("/{policy_id}")
def delete_policy(policy_id: int, db: Session = Depends(get_db)):
    policy = db.get(models.GuardrailPolicy, policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    db.delete(policy)
    db.commit()
    return {"status": "deleted"}
