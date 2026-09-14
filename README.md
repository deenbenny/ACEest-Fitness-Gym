# ACEest Fitness & Gym

A lightweight Flask REST API for tracking gym workouts, built as part of the
*Introduction to DevOps* assignment. The project demonstrates a full DevOps
lifecycle: version control, unit testing, containerization, and automated
CI/CD via GitHub Actions and Jenkins.

## Features / API Endpoints

| Method | Endpoint                    | Description                          |
|--------|------------------------------|---------------------------------------|
| GET    | `/`                          | Welcome message                       |
| GET    | `/health`                    | Health check (used by Docker/CI)      |
| GET    | `/workouts`                  | List all logged workouts              |
| POST   | `/add_workout`               | Add a workout (`{"workout": str, "duration": number}`) |
| DELETE | `/delete_workout/<id>`       | Delete a workout by id                |

Workout data is stored in memory for simplicity; it resets on restart.

## Project Structure

```
.
├── app.py                     # Flask application
├── requirements.txt           # Runtime dependencies
├── requirements-dev.txt       # Dev dependencies (pytest, flake8)
├── tests/
│   └── test_app.py            # Pytest suite
├── Dockerfile                 # Multi-stage build (base/test/final)
├── .dockerignore
├── Jenkinsfile                # Jenkins BUILD pipeline
└── .github/workflows/main.yml # GitHub Actions CI/CD pipeline
```

## Local Setup & Run

Requires Python 3.10+.

```bash
git clone https://github.com/deenbenny/ACEest-Fitness-Gym.git
cd ACEest-Fitness-Gym

python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
python app.py
```

The app runs at `http://localhost:5000`. Try it:

```bash
curl http://localhost:5000/
curl -X POST http://localhost:5000/add_workout \
     -H "Content-Type: application/json" \
     -d '{"workout": "Running", "duration": 30}'
curl http://localhost:5000/workouts
```

## Running Tests Manually

```bash
pip install -r requirements-dev.txt
pytest -v
```

Lint the code with:

```bash
flake8 app.py tests/ --max-line-length=100
```

## Running with Docker

Build and run the production image:

```bash
docker build --target final -t aceest-fitness-gym:latest .
docker run -d -p 5000:5000 aceest-fitness-gym:latest
```

Run the test stage, which installs dev dependencies and executes the
Pytest suite *inside* the container as part of the image build:

```bash
docker build --target test -t aceest-fitness-gym:test .
```

If any test fails, the `docker build` command itself fails — the image
can never be assembled from broken code.

## CI/CD Overview

### GitHub Actions (`.github/workflows/main.yml`)

Triggered on every `push` and `pull_request`, running three sequential jobs:

1. **Build & Lint** — checks out the code, installs dependencies, verifies
   the app compiles (`py_compile`), and lints with `flake8`.
2. **Automated Testing** — runs the full Pytest suite on the GitHub-hosted
   runner for fast feedback.
3. **Docker Image Assembly & Containerized Tests** — builds the Dockerfile's
   `test` stage (running Pytest *inside* the container), then builds the
   `final` production image and smoke-tests the running container via
   `/health`.

Each job only proceeds if the previous one succeeds, so a broken build never
reaches the Docker stage.

### Jenkins (`Jenkinsfile`)

Jenkins acts as a secondary, infrastructure-side BUILD quality gate,
independent of GitHub Actions:

1. **Checkout** — pulls the latest code from the configured GitHub repo.
2. **Set Up Environment** — creates a clean Python virtual environment.
3. **Lint & Syntax Check** — same checks as the GitHub Actions build-lint job.
4. **Unit Tests** — runs Pytest with JUnit XML output, published via the
   `junit` Jenkins step for test-trend reporting.
5. **Docker Build** — builds the production image, confirming the code
   integrates cleanly in the Jenkins build environment.

**Setting up Jenkins locally:**

```bash
docker run -d --name jenkins -p 8080:8080 -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  jenkins/jenkins:lts
```

Then in the Jenkins UI: **New Item → Pipeline**, set "Pipeline script from
SCM" to this repository's URL, and point it at the `Jenkinsfile` on `main`.
Configure a GitHub webhook (or poll SCM) so Jenkins triggers a BUILD on
every push.

Together, GitHub Actions provides fast, per-push/PR validation, while
Jenkins provides an independent, controlled BUILD environment as a
secondary integration check before deployment.

## Branching Strategy

Work is developed on short-lived `feature/*` and `infra/*` branches and
merged into `main` via merge commits, keeping each change scoped and the
history traceable (e.g. `feature/flask-app-init`, `feature/unit-tests`,
`feature/docker-support`, `feature/ci-pipeline`, `infra/jenkins-pipeline`).
