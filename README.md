# Lab 12: Calculator ORM Starting Template

This is the starting code for [ITCS525 Lab 12: Implement ORM in Backend APIs](https://app.notion.com/p/236dd5f44b7f80258adacc5cd3a76326).
It continues the modular calculator from Lab 8 and supplies a PostgreSQL service
and SQLModel connection setup. Ask your coding agent to implement persistence,
then review the changes and complete `lab12-report.md`.

**Starting behavior:** calculations work, but history is still an in-memory
deque, newest first, capped at 1,000 entries. Restarting the backend loses it.
`/test-db` checks PostgreSQL connectivity with `SELECT 1`; it does not create
tables. There are no session IDs or ORM tables yet.

## Run with Docker Compose

Prerequisite: Docker with Compose (for example, Docker Desktop).

```bash
cd lecture-12
cp .env.example .env
# Edit .env and replace POSTGRES_PASSWORD with a local development password.
docker compose up --build -d
```

Open http://localhost:8000/docs for the interactive API. If port 8000 is in use,
change `API_PORT` in `.env` and adjust the URLs below.

```bash
curl http://localhost:8000/test-db
# Expected: {"db_result":1}
curl -X POST http://localhost:8000/calculate \
  -H 'Content-Type: application/json' -d '{"expr":"100 - 6%"}'
# Expected: {"ok":true,"expr":{"expr":"100 - 6%"},"result":94.0,"error":""}
curl http://localhost:8000/history
curl -X DELETE http://localhost:8000/history
```

The calculation request is `{"expr":"..."}`. Evaluation errors such as `1/0`
return HTTP 200 with `ok: false` and do not enter history. A missing or incorrectly
typed `expr` returns HTTP 422. `GET /history?limit=50` clamps the limit to 0–1,000.
Arithmetic, percentages, `×`, `÷`, `−`, `pi`, and `e` follow the existing backend.

Run the baseline tests in the backend image:

```bash
docker compose exec backend pytest -q
```

After editing source files, run `docker compose up --build -d` again: this template
copies code into the image rather than using a development bind mount.

Stop the services with `docker compose down`. The named `dbdata` volume remains.
`docker compose down -v` also deletes the database data; use it only for an
intentional reset. Changing PostgreSQL credentials in `.env` does not update an
already initialized database volume.

## Run baseline tests without Docker

With Python 3.13 and [uv](https://docs.astral.sh/uv/):

```bash
uv sync --locked
uv run pytest -q
```

The baseline calculator tests need no database or `.env`. The engine is created
only when the database dependency is used. Compose supplies the database
environment automatically for the container. If running Uvicorn on the host,
export the PostgreSQL environment variables and set `DB_HOST`/`DB_PORT` to a
reachable database service; the supplied Compose database has no published port.

## Where to work

| File | Purpose |
| --- | --- |
| `app/main.py` | FastAPI application, router registration, database check |
| `app/schemas.py` | Existing Pydantic request and history response schemas |
| `app/dependencies.py` | Shared in-memory history and percentage expansion |
| `app/routers/calculator.py` | Evaluate expressions and append successful results |
| `app/routers/history.py` | Read and clear in-memory history |
| `app/database.py` | PostgreSQL engine and per-request SQLModel session dependency |
| `app/models.py` | Empty location for the table models you will add |
| `tests/test_calculator.py` | Baseline calculator and validation regression tests |
| `compose.yaml` | Backend, healthy PostgreSQL service, persistent database volume |
| `lab12-report.md` | Student report to fill in after review and verification |

`uv.lock` pins dependencies; `requirements.txt` is exported from it for Docker.
After changing dependencies, run `uv lock` and regenerate it with
`uv export --frozen --no-hashes --no-emit-project -o requirements.txt`.
Keep `.env` local; share `.env.example` with placeholders instead.

## Lab exercise

Use the prompt from the lab page with your coding agent. Your implementation
should satisfy these requirements:

- Preserve the calculation and validation behavior.
- Persist successful `POST /calculate` results with SQLModel.
- Return stored history in ascending timestamp, then id order. This replaces
  the starter's newest-first order; update that baseline test intentionally.
- Model `CalculationSession` → `CalculatorLog` as one-to-many with matching
  `back_populates` and a non-null `session_id` foreign key.
- Use server-side UTC timestamps. Start a session on the first successful
  calculation. Reuse the latest stored calculation's session for a gap of
  **10 seconds or less**; otherwise close it at its last log's timestamp and
  create another. Assume sequential requests in one global stream.
- Commit related writes together. Invalid calculations must not alter storage.
- Delete child logs when their parent is deleted; `DELETE /history` must leave
  both tables empty.
- Add table initialization after importing the table models. `create_all()`
  creates missing tables; it does not migrate existing tables.

The provided session dependency follows the [SQLModel dependency pattern](https://sqlmodel.tiangolo.com/tutorial/fastapi/session-with-dependency/).
A database session is a unit of database work; `CalculationSession` is the
domain model that groups calculations. They have different purposes.

Add deterministic tests for gaps below, exactly at, and above 10 seconds,
invalid input leaving both tables unchanged, and cascade deletion. Inject or
patch a clock rather than sleeping for the boundary tests. Keep baseline
calculation tests; adapt tests tied to the in-memory storage once it is replaced.
Use a separate disposable database for tests that modify database contents.

Verify persistence by saving a calculation, running
`docker compose restart backend`, and checking history again. Use the preserved
database volume. This check is expected to fail in the starter and pass after
your implementation. Confirm both table counts after clearing history, then
fill in the report with your own findings and supporting output.
# ITCS525-lab12
