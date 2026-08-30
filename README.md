# Blog API

Layered blog API: FastAPI + dishka (DI) + async SQLAlchemy + Postgres + Alembic.
Users write posts, posts move through a `draft → published → archived` lifecycle,
and comments are allowed only on published posts. The domain knows nothing about
the database or HTTP, use cases work through ports, and transaction boundaries
are owned by handlers.

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
├── domain/            # pure business rules, no I/O
│   ├── entities.py    #   User, Post (+ PostStatus), Comment — plain dataclasses
│   ├── services.py    #   build/patch/publish/archive + invariant validation
│   ├── constants.py   #   length limits and other invariants
│   └── exceptions.py  #   DomainError, PostStatusError, ...
├── application/       # use-case orchestration through ports
│   ├── ports.py       #   Protocols: TransactionManager, Users/Posts/CommentsPort, Gateway
│   ├── handlers/      #   one handler per use case; write handlers open a transaction
│   ├── dtos.py        #   commands/queries/DTOs (dataclasses, not pydantic)
│   ├── presenters.py  #   domain entity -> DTO
│   └── exceptions.py  #   AppError / NotFoundError / ConflictError
├── infrastructure/    # port implementations on top of SQLAlchemy
│   └── persistence/
│       ├── session.py   # engine (connection pool) + session_factory
│       ├── manager.py   # TransactionManagerImpl — transaction boundaries
│       ├── tables.py    # SQLAlchemy Core tables (no ORM models)
│       ├── adapters.py  # SQL, row -> entity mapping, error translation
│       └── gateway.py   # PersistenceGatewayImpl = manager + adapters
└── presentation/      # HTTP edge
    ├── app.py         #   app factory + error handlers
    ├── settings.py    #   pydantic-settings, env
    ├── di/            #   dishka: APP scope (engine) and REQUEST scope (session, gateway)
    └── http/          #   routes (thin glue) + pydantic schemas
```

## Domain rules

- A new post is always a `draft`; only a draft can be published; nothing leaves `archived`.
- An archived post is read-only.
- Comments are allowed only on published posts — checked inside the same transaction
  as the insert, so a post cannot be archived in between.
- Emails are normalized to lowercase; email and username are unique.
- Deleting a user cascades to their posts and comments.

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

Users:

- `POST /users` — create (409 on duplicate email/username)
- `GET /users/{id}`
- `DELETE /users/{id}` — cascades to posts and comments

Posts:

- `POST /posts` — create a draft (404 if the author does not exist)
- `GET /posts/{id}`
- `GET /posts?limit=&offset=&author_id=&status=` — list with filters
- `PATCH /posts/{id}` — partial update (409 if archived)
- `POST /posts/{id}/publish` — draft only (409 otherwise)
- `POST /posts/{id}/archive`
- `DELETE /posts/{id}`

Comments:

- `POST /posts/{id}/comments` — published posts only (409 otherwise)
- `GET /posts/{id}/comments?limit=&offset=`
- `DELETE /comments/{id}`
