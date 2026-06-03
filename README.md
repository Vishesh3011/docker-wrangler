# Two-Tier Web App Deployment with Docker & GitHub Actions

![CI/CD Pipeline](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?logo=githubactions&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![Flask](https://img.shields.io/badge/Backend-Flask-000000?logo=flask&logoColor=white)
![MySQL](https://img.shields.io/badge/Database-MySQL%208.0-4479A1?logo=mysql&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)

A fully automated CI/CD pipeline that builds, tests, and deploys a two-tier Flask + MySQL web application using GitHub Actions and Docker Compose. Every push to `main` triggers the pipeline — the app is only deployed if all tests pass.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    GitHub Actions Runner                 │
│                                                         │
│   Push to main ──► Build image ──► Run tests ──► Deploy │
└─────────────────────────────────────────────────────────┘
                                              │
                    ┌─────────────────────────┘
                    ▼
┌───────────────────────────────────────────────────────┐
│               Docker Compose Network                  │
│                                                       │
│  ┌─────────────────────┐     ┌─────────────────────┐  │
│  │  Tier 1 — Flask app │────►│  Tier 2 — MySQL 8.0 │  │
│  │  Port 5000          │     │  Internal only       │  │
│  └─────────────────────┘     └─────────────────────┘  │
└───────────────────────────────────────────────────────┘
```

**Tier 1 (Flask)** handles HTTP requests and serves the UI. It connects to MySQL using the service name `mysql` — Docker's internal DNS resolves this automatically within the Compose network.

**Tier 2 (MySQL)** persists task data in a named volume, so data survives container restarts. MySQL is not exposed to the host — only Flask can reach it.

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Application | Flask 3.0, Python 3.12 | HTTP routing, Jinja2 templating |
| Database | MySQL 8.0 | Persistent task storage |
| Containerisation | Docker, Docker Compose | Reproducible environments |
| CI/CD | GitHub Actions | Automated build, test, deploy |
| Registry | GitHub Container Registry (GHCR) | Image storage, tagged by commit SHA |
| Testing | pytest, unittest.mock | Unit tests, DB mocking |

---

## Project Structure

```
flask-mysql-app/
├── .github/
│   └── workflows/
│       └── ci.yml          # GitHub Actions pipeline
├── app/
│   ├── __init__.py
│   ├── app.py              # Flask routes
│   ├── models.py           # MySQL connection + queries
│   └── templates/
│       └── index.html      # Jinja2 template
├── tests/
│   └── test_app.py         # pytest unit tests (DB mocked)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .gitignore
```

---

## CI/CD Pipeline

The pipeline lives in `.github/workflows/ci.yml` and has two jobs:

```
git push to main
        │
        ▼
┌───────────────────┐
│  build-and-test   │  Builds Docker image → runs pytest inside container
└────────┬──────────┘  Fails here = pipeline stops, no deploy
         │ needs: build-and-test
         ▼
┌───────────────────┐
│     deploy        │  docker compose up (only on push to main, not PRs)
└───────────────────┘
```

**Key decisions:**

- Images are tagged with `github.sha` (commit hash), never `:latest` — every image is traceable to the exact commit that produced it.
- Tests run *inside* the Docker container, not on the raw runner — this proves the Dockerfile itself is correct.
- The deploy job runs only on `push` to `main`, not on pull requests. PRs trigger build + test only, so you get validation without deploying unreviewed code.
- `GITHUB_TOKEN` is used for GHCR authentication — no manual secrets needed.

---

## Running Locally

### Prerequisites

- Docker Desktop running
- Python 3.12+ (for running tests outside Docker)

### Start the full stack

```bash
# Clone the repo
git clone https://github.com/vishesh3011/flask-mysql-app.git
cd flask-mysql-app

# Start both containers (builds Flask image first)
docker compose up --build

# App is now running at http://localhost:5000
```

### Useful commands

```bash
# View running containers and health status
docker compose ps

# Stream logs from a specific service
docker compose logs -f flask
docker compose logs -f mysql

# Stop containers (data persists in named volume)
docker compose down

# Stop containers AND delete all data
docker compose down -v
```

### When to use `--build`

| Changed | Command |
|---|---|
| `.py` files or `.html` templates | `docker compose up` — reuses cached layers |
| `requirements.txt` or `Dockerfile` | `docker compose up --build` — rebuilds from scratch |
| Not sure | `docker compose up --build` — always safe, just slower |

---

## Running Tests

Tests use `unittest.mock` to patch DB calls — no MySQL instance required.

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v
```

---

## Environment Variables

The Flask app reads all config from environment variables — no hardcoded credentials anywhere. This follows the [12-Factor App](https://12factor.net/config) principle: the same image runs in dev, staging, and production with different config injected at runtime.

| Variable | Description | Default (local) |
|---|---|---|
| `MYSQL_HOST` | MySQL hostname | `localhost` |
| `MYSQL_USER` | DB username | `appuser` |
| `MYSQL_PASSWORD` | DB password | `apppassword` |
| `MYSQL_DATABASE` | Database name | `tasksdb` |

In Docker Compose these are set directly in `docker-compose.yml`. For local native runs, create a `.env` file (never commit this):

```bash
MYSQL_HOST=localhost
MYSQL_USER=appuser
MYSQL_PASSWORD=apppassword
MYSQL_DATABASE=tasksdb
```

---

## Key Concepts Demonstrated

**Docker layer caching** — `requirements.txt` is copied and installed before `COPY . .` so the expensive pip install layer is cached as long as dependencies don't change.

**Healthcheck + `depends_on`** — Flask waits until MySQL passes a `mysqladmin ping` healthcheck before starting. Without this, Flask crashes on startup because MySQL isn't ready to accept connections yet.

**Named volumes** — `mysql-data:/var/lib/mysql` persists the database across container restarts. `docker compose down` keeps it; `docker compose down -v` deletes it.

**Service discovery** — Flask connects to MySQL via hostname `mysql`, not `localhost`. Docker's internal DNS resolves service names to container IPs automatically within a Compose network.

**DB mocking in tests** — unit tests mock `get_tasks` and `add_task` so the test suite runs anywhere without a live database. This keeps tests fast, deterministic, and CI-friendly.

---

## What I Learned

- How Docker layer caching works and how Dockerfile instruction order affects build speed
- The difference between `docker compose up` and `docker compose up --build`
- Why `depends_on: condition: service_healthy` exists and how healthchecks prevent race conditions
- How GitHub Actions jobs, steps, and the `needs:` dependency chain work
- Why images should be tagged with commit SHAs instead of `:latest`
- The 12-Factor App config principle — environment-agnostic images
- How `unittest.mock` decouples unit tests from external services
