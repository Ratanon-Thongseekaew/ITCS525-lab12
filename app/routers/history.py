from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel import Session, delete, select

from app.database import get_session
from app.models import CalculationSession, CalculatorLog
from app.schemas import ExpressionOut

router = APIRouter(tags=["history"])


def convert_log_to_expression_out(log: CalculatorLog) -> ExpressionOut:
    """Convert a CalculatorLog model to ExpressionOut schema."""
    return ExpressionOut(
        expr=log.expr,
        result=log.result,
        timestamp=log.timestamp.isoformat()
    )


@router.get("/history")
def read_history(
    limit: int = 50,
    db_session: Session = Depends(get_session),
) -> list[ExpressionOut]:
    # Retrieve logs ordered by timestamp and id (ascending for proper ordering)
    logs = db_session.exec(
        select(CalculatorLog)
        .order_by(CalculatorLog.timestamp.asc(), CalculatorLog.id.asc())
        .limit(limit)
    ).all()
    
    # Convert to ExpressionOut objects
    result = [convert_log_to_expression_out(log) for log in logs]
    return result


@router.delete("/history")
def clear_history(db_session: Session = Depends(get_session)):
    # Delete all logs (which should cascade to sessions due to foreign key constraint)
    statement = delete(CalculatorLog)
    db_session.exec(statement)
    db_session.commit()
    
    return {"ok": True, "cleared": True}
