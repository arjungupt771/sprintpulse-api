# Tekravio Sprint Tracker API

FastAPI backend for Tekravio's sprint tracker assignment. The project uses async SQLAlchemy, Pydantic v2 schemas, Alembic migrations, service-layer business logic, seed data, and tests.

## Run Locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

Swagger docs are available at `http://127.0.0.1:8000/docs`.

## Run With Docker

```bash
docker compose up --build
```

The container uses PostgreSQL and applies Alembic migrations before starting the API.

## Tests

```bash
pytest --cov
```

The pytest configuration prints a terminal coverage report.

## Architecture

The app is split by responsibility:

- `app/models`: SQLAlchemy ORM entities and relationships.
- `app/schemas`: Pydantic request and response models.
- `app/services`: business rules, query composition, and computed analytics.
- `app/routers`: HTTP endpoints and status codes.
- `app/core`: settings, database session dependency, exceptions, and lightweight auth helpers.

I chose this architecture because it keeps FastAPI route functions thin while making the business logic testable without HTTP. The tradeoff is a little more ceremony than a small demo project needs, but it mirrors how enterprise APIs are maintained. At scale, I would split read-heavy analytics into query objects, add pagination metadata, introduce repository interfaces only where they reduce coupling, and move notification delivery to a queue.

## Project Health Score Formula

The health score is a 0-100 score built from four signals:

- Completion: 35 points based on the ratio of `DONE` tasks.
- Schedule: 25 points based on overdue work. Fewer overdue tasks means more points.
- Estimate accuracy: 20 points based on actual hours versus estimated hours.
- Sprint progress: 20 points based on how many project sprints are marked `DONE`.

This formula rewards delivered work but does not let a project look healthy just because tasks are marked done after running far over schedule or estimates. In a real system, I would tune weights using historical sprint outcomes and add trend data instead of scoring only the current snapshot.

## Mindset Questions

### 1. Why this architecture?

I used a conventional layered FastAPI structure because it makes the code reviewable and testable. Routers know about HTTP, services know business rules, schemas validate API boundaries, and models represent persistence. The main tradeoff is more files, but the separation pays off quickly once rules like status transitions, engineer assignment, and project health calculations appear.

### 2. What is the health score formula?

The formula combines completion, schedule risk, estimate accuracy, and sprint progress. Completion matters most, but overdue tasks and poor estimates reduce confidence. I wanted a score that can be explained to a project manager without hiding behind code.

### 3. What was hardest?

The hardest part was keeping the async SQLAlchemy relationships predictable without leaking ORM objects directly from routes. I would normally double-check SQLAlchemy eager-loading patterns and Pydantic v2 ORM serialization details, while the actual domain rules were reasoned from the assignment.

### 4. One more day?

I would add proper role-based JWT enforcement, richer test factories, and CI. The project includes the shape for auth helpers, but production-grade authorization needs careful coverage around ownership and scopes.

### 5. What am I proud of?

The sprint intelligence endpoints are not just placeholders. They compute useful signals from real task and sprint data, and the health score has a defensible formula rather than a magic number.

## Implemented Bonus Items

- Background task notification when a task is moved to `DONE`.
- CSV export at `GET /api/projects/{id}/export`.
- Dockerfile and docker-compose for FastAPI plus PostgreSQL.

