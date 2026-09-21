from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter()


@router.get("/stats", response_model=schemas.DashboardStats)
def get_stats(db: Session = Depends(get_db)):
    runs = db.query(models.TestRun).order_by(models.TestRun.id.desc()).all()
    results = db.query(models.TestCaseResult).all()

    total_cases_executed = len(results)
    total_passed = sum(1 for r in results if r.passed)
    pass_rate = (total_passed / total_cases_executed * 100) if total_cases_executed else 0.0

    breakdown: dict[str, dict[str, int]] = {}
    for result in results:
        entry = breakdown.setdefault(result.category, {"passed": 0, "failed": 0})
        if result.passed:
            entry["passed"] += 1
        else:
            entry["failed"] += 1

    return {
        "total_runs": len(runs),
        "total_cases_executed": total_cases_executed,
        "pass_rate": round(pass_rate, 2),
        "category_breakdown": breakdown,
        "recent_runs": runs[:10],
    }
