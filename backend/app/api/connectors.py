from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter()


@router.get("/", response_model=list[schemas.ConnectorOut])
def list_connectors(db: Session = Depends(get_db)):
    return db.query(models.Connector).order_by(models.Connector.id.desc()).all()


@router.post("/", response_model=schemas.ConnectorOut)
def create_connector(payload: schemas.ConnectorCreate, db: Session = Depends(get_db)):
    if payload.type not in ("http", "llm"):
        raise HTTPException(status_code=400, detail="type must be 'http' or 'llm'")
    connector = models.Connector(name=payload.name, type=payload.type, config=payload.config)
    db.add(connector)
    db.commit()
    db.refresh(connector)
    return connector


@router.get("/{connector_id}", response_model=schemas.ConnectorOut)
def get_connector(connector_id: int, db: Session = Depends(get_db)):
    connector = db.get(models.Connector, connector_id)
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")
    return connector


@router.put("/{connector_id}", response_model=schemas.ConnectorOut)
def update_connector(connector_id: int, payload: schemas.ConnectorCreate, db: Session = Depends(get_db)):
    connector = db.get(models.Connector, connector_id)
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")
    connector.name = payload.name
    connector.type = payload.type
    connector.config = payload.config
    db.commit()
    db.refresh(connector)
    return connector


@router.delete("/{connector_id}")
def delete_connector(connector_id: int, db: Session = Depends(get_db)):
    connector = db.get(models.Connector, connector_id)
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")
    db.delete(connector)
    db.commit()
    return {"status": "deleted"}


@router.post("/{connector_id}/test")
def test_connector(connector_id: int, db: Session = Depends(get_db)):
    from app.connectors.factory import build_connector

    connector = db.get(models.Connector, connector_id)
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")

    connector_type = connector.type.value if hasattr(connector.type, "value") else connector.type
    instance = build_connector(connector_type, connector.config)
    result = instance.send("Hello, this is a connectivity test message.")
    return {
        "response_text": result.response_text,
        "latency_ms": result.latency_ms,
        "error": result.error,
    }
