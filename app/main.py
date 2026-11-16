from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, text

from app.database import get_session, init_db
from app.routers import calculator, history

app = FastAPI(title="Mini Calculator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(calculator.router)
app.include_router(history.router)


@app.on_event("startup")
def startup_event():
    init_db()


@app.get("/test-db", tags=["database"])
def test_db(session: Session = Depends(get_session)):
    """Check connectivity only; this does not create tables or persist history."""
    return {"db_result": session.exec(text("SELECT 1")).scalar_one()}
