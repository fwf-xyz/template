# Notes API

Layered CRUD template: FastAPI + dishka (DI) + async SQLAlchemy + Postgres + Alembic.
The domain knows nothing about the database or HTTP, use cases work through ports,
and transaction boundaries are owned by handlers.

## Tech stack

### Runtime

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Pydantic](https://img.shields.io/badge/Pydantic-E92063?logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![Uvicorn](https://img.shields.io/badge/Uvicorn-499848?logo=uvicorn&logoColor=white)](https://www.uvicorn.org/)
[![Dishka](https://img.shields.io/badge/Dishka-DI-4B5563)](https://github.com/reagento/dishka)

[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![asyncpg](https://img.shields.io/badge/asyncpg-driver-2D3748)](https://github.com/MagicStack/asyncpg)
[![Alembic](https://img.shields.io/badge/Alembic-migrations-8A2BE2)](https://alembic.sqlalchemy.org/)

[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Docker Compose](https://img.shields.io/badge/Docker%20Compose-2496ED?logo=docker&logoColor=white)](https://docs.docker.com/compose/)

### Tooling & Quality

[![uv](https://img.shields.io/badge/uv-package%20manager-6A5ACD)](https://docs.astral.sh/uv/)
[![Ruff](https://img.shields.io/badge/Ruff-lint%2Fformat-D7FF64?logo=ruff&logoColor=black)](https://docs.astral.sh/ruff/)
[![Pytest](https://img.shields.io/badge/Pytest-tests-0A9EDC?logo=pytest&logoColor=white)](https://docs.pytest.org/)

## Layers

```
src/backend/
├── domain/            # pure business rules: Note entity, build/patch, invariants
│   ├── entities.py    #   Note dataclass — unaware of the DB and HTTP
│   ├── services.py    #   build_note / apply_note_patch + invariant validation
│   └── exceptions.py  #   DomainError
├── application/       # use-case orchestration through ports
│   ├── ports.py       #   Protocols: TransactionManager, NotesPort, PersistenceGateway
│   ├── handlers/      #   one handler per use case; write handlers open a transaction
│   ├── dtos.py        #   commands/queries/DTOs (dataclasses, not pydantic)
│   ├── presenters.py  #   domain entity -> DTO
│   └── exceptions.py  #   AppError / NotFoundError / ConflictError
├── infrastructure/    # port implementations on top of SQLAlchemy
│   └── persistence/
│       ├── session.py   # engine (connection pool) + session_factory
│       ├── manager.py   # TransactionManagerImpl — transaction boundaries
│       ├── tables.py    # SQLAlchemy Core Table (no ORM models)
│       ├── adapters.py  # SqlNotesAdapter: SQL, row -> Note mapping, error translation
│       └── gateway.py   # PersistenceGatewayImpl = manager + adapters
└── presentation/      # HTTP edge
    ├── app.py         #   app factory + error handlers
    ├── settings.py    #   pydantic-settings, env
    ├── di/            #   dishka: APP scope (engine) and REQUEST scope (session, gateway)
    └── http/          #   routes (thin glue) + pydantic schemas
```

## Getting started

```bash
docker compose up -d                  # Postgres
cp .env.example .env
uv sync                               # or: python3 -m venv .venv && .venv/bin/pip install -e . --group dev
uv run alembic upgrade head
uv run python -m backend              # http://127.0.0.1:8000/docs
```

If port 8000 is taken: `APP_PORT=8010 uv run python -m backend`.

## Checks

```bash
uv run pytest
uv run ruff check .
```

## API

- `POST /notes` — create (409 on duplicate title)
- `GET /notes/{id}` — get one
- `GET /notes?limit=&offset=` — list
- `PATCH /notes/{id}` — partial update
- `DELETE /notes/{id}` — delete
