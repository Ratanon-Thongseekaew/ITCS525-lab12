"""Lab 12 exercise: define CalculationSession and CalculatorLog tables here.

The starting template deliberately has no ORM table models. API request and
response schemas currently live in schemas.py. Follow the lab prompt to add
the one-to-many relationship, foreign key, timestamps, and deletion behavior.
"""
from datetime import datetime, timezone
from typing import List
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel


class CalculationSession(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc)) 
    ended_at: datetime | None = None
    
    # Relationship to logs - with proper setup for foreign key constraint
    logs: List["CalculatorLog"] = Relationship(back_populates="session")


class CalculatorLog(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    session_id: UUID = Field(foreign_key="calculationsession.id", ondelete="CASCADE")
    expr: str
    result: float
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Relationship to session
    session: CalculationSession = Relationship(back_populates="logs")
