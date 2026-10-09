# TraceAtlas

TraceAtlas is an early-stage data provenance and lineage application for AI/ML teams. It provides a dataset registry, CSV/Parquet profiling, version snapshots, lineage edges, downstream impact analysis, and audit events.

> **Project status:** MVP / active development. The project has been statically reviewed and updated, but the full integration test suite and Docker runtime could not be executed in this environment. Do not treat this as production-ready without running the tests and a security review.

## Features currently implemented

- Email/password registration and JWT bearer authentication.
- Automatic organization, default workspace, and owner membership creation.
- Workspace membership checks for dataset and lineage APIs.
- Dataset registration, listing, and metadata updates.
- CSV and Parquet upload and profiling (up to 50 MiB by default).
- SHA-256 content hashes, schema snapshots, missing-value counts, unique counts, numeric summaries, and duplicate-row counts.
- Dataset version history and duplicate version-tag protection.
- Lineage edge registration and graph retrieval.
- Breadth-first downstream impact traversal.
- Audit events for dataset creation/updates, version uploads, and lineage edge creation.
- Docker Compose development setup for PostgreSQL, FastAPI, and Next.js.

## Requirements

- Docker Desktop with Docker Compose v2 (recommended), or:
  - Python 3.11+
  - Node.js 18+
  - PostgreSQL 15+
- For Parquet profiling, PyArrow is installed through `backend/requirements.txt`.

## Run with Docker Compose (recommended)

1. Copy `.env.example` to `.env`.
2. Change `POSTGRES_PASSWORD` and `TRACEATLAS_SECRET_KEY` in `.env`. The included defaults are for local development only.
3. Open a terminal in the project root (the folder containing `docker-compose.yml`).
4. Build and start the services:

   ```bash
   docker compose up --build
   ```

5. Open:
   - Frontend: http://localhost:3000
   - API documentation: http://localhost:8000/docs
   - Health endpoint: http://localhost:8000/health

6. Register a user in the frontend. Registration creates a default organization and workspace.

Stop the services with `Ctrl+C`, or run `docker compose down`. Database data is stored in the `pgdata` Docker volume. To remove that volume too, use `docker compose down -v` (this permanently deletes the local database).

## Run the backend without Docker

From the `backend` directory:

1. Create and activate a Python virtual environment.
2. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

3. Create `backend/.env` with values appropriate for your environment, for example:

   ```env
   DATABASE_URL=postgresql+asyncpg://traceatlas:your-password@localhost:5432/traceatlas
   SECRET_KEY=replace-with-a-long-random-secret
   UPLOAD_DIR=./uploads
   MAX_UPLOAD_BYTES=52428800
   CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
   ```

4. Start the API:

   ```bash
   uvicorn app.main:app --reload
   ```

The app currently calls SQLAlchemy `create_all()` at startup to make local MVP setup easier. Alembic configuration is included, but a complete production migration history should be generated and reviewed before production deployment.

## Run the frontend without Docker

From the `frontend` directory:

```bash
npm install
```

Set `NEXT_PUBLIC_API_URL` to the backend origin, for example `http://localhost:8000`, then run:

```bash
npm run dev
```

Open http://localhost:3000. The API URL is public client configuration; never put credentials or private keys in `NEXT_PUBLIC_*` variables.

## Run automated tests

From the `backend` directory after installing the requirements:

```bash
pytest -q
```

The tests use an in-memory SQLite database and a temporary upload directory. They cover registration/login, password validation, dataset creation and profiling, duplicate version tags, workspace isolation, and lineage impact behavior.

## API overview

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/auth/register` | Create user, organization, workspace, and membership |
| POST | `/api/auth/login` | Obtain JWT (JSON body: email and password) |
| GET | `/api/auth/me` | Get current user |
| GET | `/api/auth/workspaces` | List workspaces for current user |
| POST | `/api/datasets/?workspace_id=...` | Register dataset |
| GET | `/api/datasets/?workspace_id=...` | List workspace datasets |
| GET | `/api/datasets/{id}` | Get dataset passport |
| PATCH | `/api/datasets/{id}` | Update dataset metadata |
| POST | `/api/datasets/{id}/versions?version_tag=...` | Upload and profile CSV/Parquet |
| GET | `/api/datasets/{id}/versions` | List version snapshots |
| POST | `/api/lineage/edges?workspace_id=...` | Register a lineage edge |
| GET | `/api/lineage/graph?workspace_id=...` | Get workspace lineage graph |
| GET | `/api/lineage/impact?...` | Find downstream assets |

Authenticated endpoints require `Authorization: Bearer <token>`.

## Important limitations

- This is not yet a complete data governance or compliance platform.
- Current lineage asset validation supports datasets, dataset versions, models, and model versions. Other asset types are declared in the model but are not yet fully implemented.
- Dataset file contents are stored on the backend upload volume. Backups, retention policies, malware scanning, and object-storage integration still need implementation.
- Uploads are limited by file size, but profiling large datasets can still consume significant CPU and memory. Add streaming/incremental profiling and stronger resource limits before accepting untrusted production uploads.
- The UI currently uses browser local storage for the JWT. For production, consider secure HttpOnly cookie sessions, CSRF protections where relevant, and a formal token refresh/revocation strategy.
- Governance status is metadata, not a legal determination.
- The default development secret and database password must be replaced before any public deployment.
- Role values are stored, but fine-grained per-role authorization policies still need implementation.
- The application needs a full production security review, database migrations, deployment hardening, monitoring, backups, and end-to-end tests before real customer data is used.

## Repository layout

```text
TraceAtlas/
├── docker-compose.yml
├── .env.example
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── services/
│   ├── migrations/
│   ├── tests/
│   └── requirements.txt
└── frontend/
    ├── src/app/
    ├── src/components/
    ├── src/lib/
    └── package.json
```

## License

No license is currently specified. Add a license file before accepting external contributions or distributing the project.
