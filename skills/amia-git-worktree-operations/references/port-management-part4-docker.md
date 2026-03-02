# Port Management - Part 4: Docker Compose Integration

## Table of Contents

1. [When you need dynamic Docker port mapping → Docker Compose Integration](#docker-compose-integration)
   - 1.1 [Why Docker Compose Integration?](#why-docker-compose-integration)
   - 1.2 [Dynamic Port Mapping Strategy](#dynamic-port-mapping-strategy)
   - 1.3 [Example: Single Service](#example-single-service)
   - 1.4 [Example: Multiple Services](#example-multiple-services)
   - 1.5 [Automation Script](#automation-script)
   - 1.6 [Cleanup on Stop](#cleanup-on-stop)

**Related Parts:**
- [Part 1: Overview and Registry Structure](port-management-part1-overview-registry.md)
- [Part 2: Allocation Functions and CLI](port-management-part2-allocation-cli.md)
- [Part 3: Conflict Detection and Health Checking](port-management-part3-conflicts-health.md)
- [Part 5: Troubleshooting](port-management-part5-troubleshooting.md)

---

## Docker Compose Integration

Docker Compose services can be configured to use dynamically allocated ports from the registry.

### Why Docker Compose Integration?

When running Docker containers in multiple worktrees:
- Each worktree needs its own container instances
- Containers must expose services on different ports
- Port mappings must be configured dynamically

### Dynamic Port Mapping Strategy

**Approach:** Use environment variables to pass allocated ports to Docker Compose.

**Steps:**
1. Allocate ports using the port management system
2. Export ports as environment variables
3. Reference environment variables in `docker-compose.yml`
4. Start Docker Compose with the environment variables

### Example: Single Service

**Step 1: Allocate Port**
```bash
# Allocate a web server port
PORT_WEB=$(python scripts/port_allocate.py --service web --worktree review-GH-42 --quiet)
echo "Allocated web port: $PORT_WEB"
```

**Step 2: Export as Environment Variable**
```bash
export PORT_WEB
```

**Step 3: Configure docker-compose.yml**
```yaml
version: '3.8'

services:
  web:
    image: nginx:latest
    ports:
      - "${PORT_WEB}:80"
    environment:
      - PORT=${PORT_WEB}
```

**Step 4: Start Docker Compose**
```bash
docker-compose up -d
```

The nginx container will be accessible at `http://localhost:$PORT_WEB`.

### Example: Multiple Services

**Step 1: Allocate Multiple Ports**
```bash
# Allocate ports for different services
PORT_WEB=$(python scripts/port_allocate.py --service web --worktree review-GH-42 --description "Nginx web server" --quiet)
PORT_API=$(python scripts/port_allocate.py --service api --worktree review-GH-42 --description "FastAPI backend" --quiet)
PORT_DB=$(python scripts/port_allocate.py --service database --worktree review-GH-42 --description "PostgreSQL database" --quiet)

echo "Web: $PORT_WEB"
echo "API: $PORT_API"
echo "DB: $PORT_DB"
```

**Step 2: Create .env File**
```bash
cat > .env << EOF
PORT_WEB=$PORT_WEB
PORT_API=$PORT_API
PORT_DB=$PORT_DB
EOF
```

**Step 3: Configure docker-compose.yml**
```yaml
version: '3.8'

services:
  web:
    image: nginx:latest
    ports:
      - "${PORT_WEB}:80"
    depends_on:
      - api
    environment:
      - API_URL=http://localhost:${PORT_API}

  api:
    image: myapp/api:latest
    ports:
      - "${PORT_API}:8000"
    depends_on:
      - db
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/myapp

  db:
    image: postgres:14
    ports:
      - "${PORT_DB}:5432"
    environment:
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=myapp
```

**Step 4: Start Docker Compose**
```bash
docker-compose --env-file .env up -d
```

Services are now accessible at:
- Web: `http://localhost:$PORT_WEB`
- API: `http://localhost:$PORT_API`
- DB: `localhost:$PORT_DB`

### Automation Script

Create a helper script `scripts/docker_start.sh`:

```bash
#!/bin/bash
set -e

WORKTREE_NAME=$(basename "$PWD")

echo "Starting Docker services for worktree: $WORKTREE_NAME"

# Allocate ports
PORT_WEB=$(python scripts/port_allocate.py --service web --worktree "$WORKTREE_NAME" --description "Web server" --quiet)
PORT_API=$(python scripts/port_allocate.py --service api --worktree "$WORKTREE_NAME" --description "API server" --quiet)
PORT_DB=$(python scripts/port_allocate.py --service database --worktree "$WORKTREE_NAME" --description "Database" --quiet)

# Create .env file
cat > .env << EOF
PORT_WEB=$PORT_WEB
PORT_API=$PORT_API
PORT_DB=$PORT_DB
EOF

echo "Allocated ports:"
echo "  Web: $PORT_WEB"
echo "  API: $PORT_API"
echo "  DB:  $PORT_DB"

# Start Docker Compose
docker-compose --env-file .env up -d

echo "Services started successfully"
echo "  Web: http://localhost:$PORT_WEB"
echo "  API: http://localhost:$PORT_API"
echo "  DB:  localhost:$PORT_DB"
```

**Usage:**
```bash
# Make script executable
chmod +x scripts/docker_start.sh

# Run from worktree directory
./scripts/docker_start.sh
```

### Cleanup on Stop

Create a helper script `scripts/docker_stop.sh`:

```bash
#!/bin/bash
set -e

WORKTREE_NAME=$(basename "$PWD")

echo "Stopping Docker services for worktree: $WORKTREE_NAME"

# Stop Docker Compose
docker-compose down

# Release allocated ports
python scripts/port_status.py --worktree "$WORKTREE_NAME" --format json | \
  jq -r '.[].port' | \
  while read -r port; do
    python scripts/port_allocate.py --release "$port"
    echo "Released port: $port"
  done

# Remove .env file
rm -f .env

echo "Services stopped and ports released"
```

**Usage:**
```bash
# Make script executable
chmod +x scripts/docker_stop.sh

# Run from worktree directory
./scripts/docker_stop.sh
```

---

**Continue to:** [Part 5: Troubleshooting](port-management-part5-troubleshooting.md)

**Last Updated:** 2025-12-31
