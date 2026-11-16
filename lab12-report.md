# Lab 12: ORM Code Review Report

- Name: Ratanon Thongseekaew
- Student ID: 6938712
- Coding agent used: qwen/qwen3-coder-30b-a3b-instruct

## Code Review

### 1. Table Models and API Schemas

Which classes are database tables, and which are API schemas?

- CalculationSession and CalculatorLog are database tables because they inherit from SQLModel with table=True (app/models.py, lines 14–31).

- BaseExpression, ExpressionIn, and ExpressionOut are Pydantic API schemas (app/schemas.py, lines 7–21).


### 2. Keys and Relationships

Where are the primary key, foreign key, and relationship defined?

- The primary keys are CalculationSession.id and CalculatorLog.id, defined with primary_key=True (app/models.py, lines 15 and 24).

- The foreign key is CalculatorLog.session_id, which references calculationsession.id and specifies ondelete="CASCADE" (app/models.py, line 25).

- The one-to-many relationship is defined by CalculationSession.logs and CalculatorLog.session, using matching back_populates values (app/models.py, lines 20 and 31).

### 3. Database Operations

Where does each endpoint read, insert, or delete records?

POST /calculate reads the latest session in get_latest_session(), inserts a session in create_new_session(), and inserts a calculation log in calculate() (app/routers/calculator.py, lines 18–31 and 48–86).

GET /history reads calculation logs and orders them by timestamp and ID (app/routers/history.py, lines 24–38).

DELETE /history deletes calculation logs and commits the change (app/routers/history.py, lines 41–47).

GET /test-db executes SELECT 1 to test database connectivity (app/main.py, lines 21–24).

## One Review Finding

Describe one correction you requested OR one design choice you independently
verified. You do not need to invent a defect.

- Finding: The session-gap logic does not correctly create a new session after a gap longer than 10 seconds.
 
- Correction made or reason for accepting the design: The latest calculation timestamp should be compared with the current time. A gap of 10 seconds or less should reuse the session; a gap longer than 10 seconds should close the previous session and create a new one.

- Code or test evidence: get_latest_session() only selects sessions whose ended_at is None, but calculate() checks the time gap only when ended_at has a value. Therefore, the returned active session cannot satisfy the gap condition (app/routers/calculator.py, lines 18–22 and 48–61).

## Verification

### 1. Calculations Within 10 Seconds
Expected: the same session ID.

Passes

### 2. Gap Longer Than 10 Seconds
Expected: a new session ID.

Passes

### 3. Exactly 10 Seconds Apart
Expected: the same session ID, verified by an automated test.

Failed

### 4. Backend Restart
Expected: history remains when the database volume is preserved.

Passes

### 5. Clear History
Expected: both session and log tables are empty.

Failed

### Notes
At the first prompt, it only passed one test. Although I tried to fix the result by adding
a new prompt but seem like it also cannot fix it in one shot.
