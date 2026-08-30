# Notes API — учебный CRUD-шаблон

FastAPI + dishka (DI) + SQLAlchemy (async) + Postgres + Alembic.
Слоистая архитектура: домен не знает про БД и HTTP, use-case'ы работают через порты,
границами транзакций владеют хендлеры.

## Слои

```
src/backend/
├── domain/            # чистые бизнес-правила: сущность Note, build/patch, инварианты
│   ├── entities.py    #   dataclass Note — не знает ни про БД, ни про HTTP
│   ├── services.py    #   build_note / apply_note_patch + валидация инвариантов
│   └── exceptions.py  #   DomainError
├── application/       # оркестрация use-case'ов через порты
│   ├── ports.py       #   Protocol'ы: TransactionManager, NotesPort, PersistenceGateway
│   ├── handlers/      #   по хендлеру на use-case; write-хендлеры открывают транзакцию
│   ├── dtos.py        #   команды/запросы/DTO (dataclass'ы, не pydantic)
│   ├── presenters.py  #   доменная сущность -> DTO
│   └── exceptions.py  #   AppError / NotFoundError / ConflictError
├── infrastructure/    # реализация портов поверх SQLAlchemy
│   └── persistence/
│       ├── session.py   # engine (пул) + session_factory
│       ├── manager.py   # TransactionManagerImpl — границы транзакций
│       ├── tables.py    # SQLAlchemy Core Table (без ORM-моделей)
│       ├── adapters.py  # SqlNotesAdapter: SQL, маппинг строк -> Note, перевод ошибок
│       └── gateway.py   # PersistenceGatewayImpl = manager + адаптеры
└── presentation/      # HTTP-край
    ├── app.py         #   фабрика приложения + error handler'ы
    ├── settings.py    #   pydantic-settings, env
    ├── di/            #   dishka: APP-scope (engine) и REQUEST-scope (session, gateway)
    └── http/          #   ручки (тонкий клей) + pydantic-схемы
```

## Путь запроса (например, `PATCH /notes/{id}`)

1. **Ручка** ([routing/notes.py](src/backend/presentation/http/routing/notes.py)) — получает
   из DI готовый `PersistenceGateway`, переливает pydantic-схему в команду-DTO,
   создаёт хендлер и вызывает его. Логики в ручке нет.
2. **DI** ([di/providers.py](src/backend/presentation/di/providers.py)) — dishka резолвит цепочку:
   `session_factory` (APP-scope, один на процесс) → `AsyncSession` (REQUEST-scope,
   **одна сессия на запрос**, закрывается после ответа) → `PersistenceGatewayImpl(session)`.
3. **Хендлер** ([handlers/notes.py](src/backend/application/handlers/notes.py)) — открывает
   границу транзакции `async with gateway.manager.transaction():` и внутри неё:
   читает сущность → мутирует через доменный сервис (валидация инвариантов) → сохраняет.
   Упал любой шаг — rollback всего.
4. **Адаптер** ([persistence/adapters.py](src/backend/infrastructure/persistence/adapters.py)) —
   выполняет SQL на той же сессии, маппит строки в доменную `Note`, переводит
   `IntegrityError` → `ConflictError`, «нет строки» → `NotFoundError`. Транзакциями не управляет.
5. **Ошибки** — на HTTP-краю ([app.py](src/backend/presentation/app.py)) два хендлера:
   `AppError` → статус из ошибки (404/409/…), `DomainError` → 400.

## Ключевые решения (и почему)

- **Сессия ≠ транзакция.** Сессия живёт весь запрос (REQUEST-scope в DI), транзакция —
  коротко, только внутри write-хендлера. Read-хендлеры транзакцию не открывают.
- **Границы транзакции задаёт use-case, а не CRUD.** Адаптеры ничего не коммитят —
  иначе нельзя собрать несколько операций в одну атомарную (см. `UpdateNoteHandler`).
- **Application зависит от `Protocol`-портов, а не от SQLAlchemy** — хендлеры тестируются
  фейками без БД (см. [tests/test_note_handlers.py](tests/test_note_handlers.py)).
- **Ошибки переводятся на границах**: SQLAlchemy-исключения не поднимаются выше адаптера,
  доменные — выше HTTP-края.
- **Валидация формы — на краю (pydantic), инварианты — в домене** (`build_note` / `apply_note_patch`).

## Запуск

```bash
docker compose up -d                  # Postgres
cp .env.example .env
uv sync                               # или: python3 -m venv .venv && .venv/bin/pip install -e . --group dev
uv run alembic upgrade head
uv run python -m backend              # http://127.0.0.1:8000/docs
```

Если порт 8000 занят: `APP_PORT=8010 uv run python -m backend`.

## Проверки

```bash
uv run pytest
uv run ruff check .
```

## API

- `POST /notes` — создать (409 при дубле title)
- `GET /notes/{id}` — получить
- `GET /notes?limit=&offset=` — список
- `PATCH /notes/{id}` — частичное обновление
- `DELETE /notes/{id}` — удалить
