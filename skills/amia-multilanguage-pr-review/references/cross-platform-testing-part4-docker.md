# Cross-Platform Testing: Part 4 - Using Docker for Reproducible Builds

## Table of Contents

- 7.4.1 Multi-platform Docker build with multi-stage
- 7.4.2 GitHub Actions with Docker services
- 7.4.3 Multi-architecture builds (amd64, arm64)
- 7.4.4 Docker Compose for testing
- 7.4.5 Development containers (devcontainer)
- 7.4.6 Docker testing checklist

---

## 7.4 Using Docker for Reproducible Builds

Docker ensures consistent build environments across platforms.

### Multi-Platform Docker Build

```dockerfile
# Dockerfile
FROM --platform=$BUILDPLATFORM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
COPY src/ src/

RUN pip wheel --no-deps --wheel-dir /wheels .

# Runtime image
FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /wheels /wheels
RUN pip install --no-cache /wheels/*.whl

COPY . .

CMD ["python", "-m", "myapp"]
```

### GitHub Actions with Docker

```yaml
jobs:
  docker-test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    container:
      image: python:3.12-slim

    steps:
      - uses: actions/checkout@v4

      - name: Install dependencies
        run: pip install -e ".[dev]"

      - name: Run tests
        run: pytest
        env:
          DATABASE_URL: postgres://postgres:postgres@postgres:5432/test
```

### Multi-Architecture Builds

```yaml
# .github/workflows/docker.yml
name: Docker Build

on:
  push:
    tags: ['v*']

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up QEMU
        uses: docker/setup-qemu-action@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          platforms: linux/amd64,linux/arm64
          push: true
          tags: myorg/myapp:${{ github.ref_name }}
```

### Docker Compose for Testing

```yaml
# docker-compose.test.yml
version: '3.8'

services:
  test:
    build:
      context: .
      dockerfile: Dockerfile.test
    depends_on:
      - db
      - redis
    environment:
      DATABASE_URL: postgres://postgres:postgres@db:5432/test
      REDIS_URL: redis://redis:6379
    command: pytest

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: test

  redis:
    image: redis:7-alpine
```

```bash
# Run tests in Docker
docker compose -f docker-compose.test.yml up --build --exit-code-from test
```

### Development Container (devcontainer)

```json
// .devcontainer/devcontainer.json
{
  "name": "Python Development",
  "image": "mcr.microsoft.com/devcontainers/python:3.12",
  "features": {
    "ghcr.io/devcontainers/features/node:1": {},
    "ghcr.io/devcontainers/features/rust:1": {}
  },
  "postCreateCommand": "pip install -e '.[dev]'",
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "charliermarsh.ruff"
      ]
    }
  },
  "forwardPorts": [8000],
  "remoteUser": "vscode"
}
```

### Docker Testing Checklist

- [ ] Dockerfile uses multi-stage builds
- [ ] Base images are pinned to specific versions
- [ ] Tests run in isolated containers
- [ ] Services (DB, cache) are containerized
- [ ] Multi-architecture builds configured
- [ ] Development containers available for contributors
- [ ] Docker Compose available for local testing
- [ ] CI uses same Docker configuration as local

---

**Previous**: [Part 3 - Platform-Specific Test Skips](cross-platform-testing-part3-test-skips.md)

**Back to Index**: [Cross-Platform Testing Reference](cross-platform-testing.md)
