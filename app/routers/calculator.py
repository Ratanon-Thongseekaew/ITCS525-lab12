import math
from datetime import datetime, timezone
from uuid import UUID

from asteval import Interpreter
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.dependencies import expand_percent, get_history
from app.models import CalculationSession, CalculatorLog
from app.schemas import ExpressionIn, ExpressionOut

router = APIRouter(tags=["calculator"])


def get_latest_session(session: Session) -> CalculationSession | None:
    """Get the latest active session."""
    statement = select(CalculationSession).where(CalculationSession.ended_at.is_(None)).order_by(CalculationSession.created_at.desc()).limit(1)
    return session.exec(statement).first()


def create_new_session(session: Session) -> CalculationSession:
    """Create a new calculation session."""
    new_session = CalculationSession()
    session.add(new_session)
    session.commit()
    session.refresh(new_session)
    return new_session


@router.post("/calculate")
def calculate(
    expr: ExpressionIn,
    code: str = Depends(expand_percent),
    db_session: Session = Depends(get_session),
):
    try:
        # Each calculation gets its own evaluator and error state.
        aeval = Interpreter(minimal=True, usersyms={"pi": math.pi, "e": math.e})
        result = aeval(code)
        if aeval.error:
            msg = "; ".join(str(e.get_error()) for e in aeval.error)
            return {"ok": False, "expr": expr, "result": "", "error": msg}
        
        # Get or create a session
        latest_session = get_latest_session(db_session)
        current_time = datetime.now(timezone.utc)
        
        # Determine which session to use
        if latest_session is None:
            # First calculation - create new session
            calc_session = create_new_session(db_session)
        else:
            # Check if we should reuse the session or create a new one
            # Find the latest log in the current session to determine the gap
            latest_log_statement = select(CalculatorLog).where(CalculatorLog.session_id == latest_session.id).order_by(CalculatorLog.timestamp.desc()).limit(1)
            latest_log = db_session.exec(latest_log_statement).first()
            
            if latest_log is None:
                # No logs in existing session - reuse it
                calc_session = latest_session
            else:
                # Calculate the time gap from the latest log
                gap_seconds = (current_time - latest_log.timestamp).total_seconds()
                
                if gap_seconds <= 10:
                    # Gap less than or equal to 10 seconds - reuse session 
                    calc_session = latest_session
                else:
                    # Gap exceeds 10 seconds - close current session and create a new one
                    latest_session.ended_at = latest_log.timestamp
                    calc_session = create_new_session(db_session)
        
        # Only save successful calculations
        log_entry = CalculatorLog(
            session_id=calc_session.id,
            expr=expr.expr,
            result=result,
            timestamp=current_time
        )
        
        # Save everything together in a single transaction
        try:
            db_session.add(log_entry)
            db_session.commit()
            db_session.refresh(log_entry)
            
            # Update in-memory history as before (for compatibility with existing tests) 
            # This is kept for backward compatibility with existing tests 
            history = get_history()
            history.appendleft(ExpressionOut(expr=expr.expr, result=result))
            
            return {"ok": True, "expr": expr, "result": result, "error": ""}
        except Exception:
            # If there was an error saving to the DB, rollback the transaction
            db_session.rollback()
            raise
            
    except Exception as exc:
        return {"ok": False, "expr": expr, "error": str(exc)}
