# SprintPulse API

**A Python backend for sprint tracking, project-health analytics, and delivery insights.**

SprintPulse is a FastAPI application built around project, client, engineer, sprint, and task management. It combines asynchronous database operations with service-layer business logic and a weighted health score to make project progress easier to understand.

Originally developed as a Tekravio sprint-tracker assignment, this project demonstrates backend API design, database modeling, validation, testing, and business-rule implementation.

## Features

- **REST API:** Manage clients, engineers, projects, sprints, and tasks.
- **Project health analytics:** Calculate a 0–100 health score from completion, schedule risk, estimate accuracy, and sprint completion.
- **Sprint intelligence:** Derive useful delivery metrics from task and sprint data.
- **Task notifications:** Trigger background notifications when a task moves to `DONE`.
- **CSV export:** Export project task data for reporting and analysis.
- **Database migrations:** Manage schema changes with Alembic.
- **Containerized setup:** Run the API with Docker Compose and PostgreSQL.
- **Automated tests:** Validate API behavior and important business rules.

## Tech Stack

- **Language:** Python
- **API:** FastAPI, Uvicorn
- **Database:** SQLAlchemy 2.x, async database access
- **Validation:** Pydantic v2
- **Migrations:** Alembic
- **Testing:** Pytest, pytest-asyncio, pytest-cov
- **Containerization:** Docker, Docker Compose

## Getting Started

### Prerequisites

- Python 3.10 or newer
- Git
- Docker and Docker Compose, if using the containerized setup

### Run locally on Linux or macOS

Clone the repository and enter the project directory:

```bash
git clone https://github.com/arjungupt771/sprintpulse-api.git
cd sprintpulse-api
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the project and development dependencies:

```bash
python -m pip install -e ".[dev]"
```

Apply database migrations and load the seed data:

```bash
alembic upgrade head
python -m app.seed
```

Start the development server:

```bash
uvicorn app.main:app --reload
```

### Run locally on Windows

Activate the virtual environment using PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

If PowerShell blocks script activation, use Command Prompt and run `.venv\Scripts\activate.bat` instead.

**Configuration:** Use the database settings defined by the application. For the Docker setup, the database service uses PostgreSQL.

## API Documentation

Once the server is running, open:

- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

The interactive documentation lets you inspect endpoints, schemas, request parameters, and responses.

## Run With Docker

Build and start the services:

```bash
docker compose up --build
```

The containerized setup uses PostgreSQL and applies Alembic migrations before starting the API.

Stop the services with:

```bash
docker compose down
```

## Run Tests

Activate your virtual environment and run:

```bash
PYTHONPATH=. pytest -q
```

To display test coverage:

```bash
PYTHONPATH=. pytest
```

The pytest configuration enables coverage reporting for the `app` package. The development dependencies include the required coverage plugin.

## Architecture

The application follows a layered structure:

| Directory | Responsibility |
|---|---|
| `app/routers` | HTTP endpoints, request handling, and response models |
| `app/services` | Business logic, database queries, and computed analytics |
| `app/models` | SQLAlchemy entities and relationships |
| `app/schemas` | Pydantic request and response validation |
| `app/core` | Configuration, database sessions, exceptions, and security helpers |

This separation keeps route handlers relatively thin and makes business rules easier to test independently of HTTP concerns.

The trade-off is additional structure compared with a small single-file application, but it improves readability as domain logic grows.

## Project Health Score

The project health score ranges from 0 to 100 and combines four weighted signals:

| Signal | Maximum points | Calculation |
|---|---:|---|
| Task completion | 35 | Proportion of tasks marked `DONE` |
| Schedule health | 25 | Fewer overdue, unfinished tasks yield more points |
| Estimate accuracy | 20 | Penalizes the magnitude of task-level estimation errors |
| Sprint completion | 20 | Proportion of project sprints marked `DONE` |

The estimate-accuracy component uses the sum of absolute differences between actual and estimated hours for individual tasks, divided by total estimated hours. This prevents overestimates and underestimates from cancelling each other out.

The error ratio is capped at 100%, and the resulting estimate-accuracy points are calculated as:

`20 × (1 − min(total absolute estimation error / total estimated hours, 1))`

When total estimated hours are zero, the current implementation awards the full 20 estimate-accuracy points.

The weights are explicit and explainable rather than hidden in an opaque score. In a real-world product, they could be calibrated against historical sprint outcomes.

## Design Decisions

**Why a service layer?**

Routes focus on HTTP concerns, while services own business rules and database operations. This makes the application easier to review, test, and extend without coupling every rule to a route handler.

**Why asynchronous SQLAlchemy?**

Async database access fits FastAPI's asynchronous request-handling model and supports efficient I/O-bound operations.

**What was challenging?**

Managing ORM relationships, asynchronous queries, and Pydantic v2 response serialization required care. These boundaries are particularly important when returning nested project, sprint, and task data.

**What would I improve next if needed?**

Potential future work includes stronger authorization enforcement, broader service-level test coverage, and continuous integration. These are deliberately separate from the current project's core scope.

## Project Scope

This repository focuses on backend functionality, clear business logic, and maintainable code. It is not presented as a fully production-hardened service: authentication and authorization enforcement should be reviewed and strengthened before use in a real multi-user environment.

## License

Add a license file if you intend to distribute or reuse this project under explicit open-source terms.
