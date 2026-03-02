# Docker Worktree Testing - Part 1: Setup & Configuration

## Table of Contents

1. [When you need to understand Docker with worktrees - Overview](#overview)
   - [If you're wondering why combine Docker and worktrees - Why Combine?](#why-combine-docker-with-worktrees)
   - [When you need to know when to use this - Use Cases](#use-cases)
2. [When you need one container set per worktree - Container-Per-Worktree Pattern](#container-per-worktree-pattern)
   - [If you need pattern overview - Pattern Components](#pattern-components)
   - [When you want to understand the mechanism - How It Works](#how-it-works)
   - [If you need naming guidelines - Container Naming Convention](#container-naming-convention)
3. [When you need Docker Compose configuration - Docker Compose Per Worktree](#docker-compose-per-worktree)
   - [If you need template structure - Template Structure](#template-structure)
   - [When you need template details - Template Explanation](#template-explanation)
4. [When you need dynamic ports - Dynamic Port Configuration](#dynamic-port-configuration)
   - [If you need port assignment process - Port Assignment Flow](#port-assignment-flow)
   - [When generating environment files - Environment File Generation](#environment-file-generation)
   - [If avoiding port conflicts - Port Conflict Avoidance](#port-conflict-avoidance)
5. [When you need a complete example - Workflow Example](#workflow-example)

**Related Documentation:**
- [Part 2: Best Practices & Troubleshooting](docker-worktree-testing-part2-best-practices.md) - Resource limits, cleanup, health checks, common problems

---

## Overview

**Docker worktree testing** is the practice of combining Git worktrees with Docker containers to create isolated testing environments. Each worktree can run its own set of containers without interfering with other worktrees or the main development environment.

### Why Combine Docker with Worktrees?

1. **Complete Isolation**: Each worktree gets its own database, services, and runtime environment
2. **No Port Conflicts**: Different worktrees use different ports for their services
3. **Parallel Testing**: Run integration tests in multiple branches simultaneously
4. **Clean State**: Each worktree starts with fresh containers and data
5. **Reproducibility**: Consistent environment across all worktrees

### Use Cases

- Integration testing across multiple feature branches
- Testing database migrations in isolation
- Running different service versions simultaneously
- Performance testing without affecting development environment
- Regression testing on hotfix branches

---

## Container-Per-Worktree Pattern

The **Container-Per-Worktree Pattern** means each worktree directory runs its own isolated set of Docker containers. These containers are separate from containers in other worktrees and from the main repository.

### Pattern Components

1. **Worktree Directory**: The isolated Git working directory
2. **Container Set**: All Docker containers needed for that worktree (app, database, cache, etc.)
3. **Port Allocation**: Unique ports assigned to avoid conflicts
4. **Volume Mount**: The worktree directory mounted into containers

### How It Works

```
Main Repo (localhost:3000, 5432)
├── Container: app-main
├── Container: db-main
└── Container: redis-main

Worktree: test-int-api (localhost:8081, 5433, 6380)
├── Container: app-test-int-api
├── Container: db-test-int-api
└── Container: redis-test-int-api

Worktree: test-auth-fix (localhost:8082, 5434, 6381)
├── Container: app-test-auth-fix
├── Container: db-test-auth-fix
└── Container: redis-test-auth-fix
```

### Container Naming Convention

Use this naming pattern for containers:
```
<service>-<worktree-identifier>
```

Examples:
- `app-test-int-api` (app service in test-int-api worktree)
- `db-hotfix-security` (database in hotfix-security worktree)
- `redis-feat-caching` (Redis in feat-caching worktree)

This naming prevents container name conflicts and makes it clear which worktree owns each container.

---

## Docker Compose Per Worktree

Each worktree should have its own Docker Compose configuration that can be customized with environment variables for ports and other settings.

### Template Structure

Create a `docker-compose.worktree.yml` template file in your main repository:

```yaml
# docker-compose.worktree.yml
# Template for worktree-specific Docker environments
# Copy this to each worktree and customize via .env.docker

version: '3.8'

services:
  app:
    # Application service
    build:
      context: .
      dockerfile: Dockerfile
    container_name: app-${WORKTREE_ID:-main}
    ports:
      # Map external port (from env) to internal port 8080
      - "${WEB_PORT:-8080}:8080"
    volumes:
      # Mount worktree directory to /app in container
      - .:/app
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/mydb
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    networks:
      - worktree-net

  db:
    # PostgreSQL database service
    image: postgres:15
    container_name: db-${WORKTREE_ID:-main}
    ports:
      # Map external port (from env) to internal PostgreSQL port 5432
      - "${DB_PORT:-5432}:5432"
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=mydb
    volumes:
      # Persist database data (unique per worktree)
      - db-data-${WORKTREE_ID:-main}:/var/lib/postgresql/data
    networks:
      - worktree-net

  redis:
    # Redis cache service
    image: redis:7-alpine
    container_name: redis-${WORKTREE_ID:-main}
    ports:
      # Map external port (from env) to internal Redis port 6379
      - "${REDIS_PORT:-6379}:6379"
    networks:
      - worktree-net

networks:
  # Isolated network per worktree
  worktree-net:
    name: net-${WORKTREE_ID:-main}
    driver: bridge

volumes:
  # Named volume for database persistence
  db-data-${WORKTREE_ID:-main}:
    name: db-data-${WORKTREE_ID:-main}
```

### Template Explanation

**Key Features:**

1. **Variable Substitution**: Uses `${VAR:-default}` syntax
   - `${WEB_PORT:-8080}`: Use WEB_PORT from environment, fallback to 8080
   - `${WORKTREE_ID:-main}`: Use WORKTREE_ID from environment, fallback to "main"

2. **Port Mapping**: `"external:internal"` format
   - External port varies per worktree (from environment)
   - Internal port stays fixed (what app expects inside container)

3. **Volume Mounting**: `.:/app` mounts worktree directory to `/app` in container
   - Changes in worktree immediately reflected in container
   - No need to rebuild for code changes

4. **Container Names**: Include `${WORKTREE_ID}` to prevent conflicts

5. **Network Isolation**: Each worktree gets its own Docker network

---

## Dynamic Port Configuration

To run multiple worktrees simultaneously, each must use different external ports. The worktree port allocation system provides these ports automatically.

### Port Assignment Flow

1. **Create worktree with ports**:
   ```bash
   python scripts/worktree_create.py --purpose test --identifier int-api --branch feat --ports
   ```

2. **System allocates ports** and stores in `allocated_ports.json`:
   ```json
   {
     "test-int-api": {
       "web": 8081,
       "db": 5433,
       "redis": 6380
     }
   }
   ```

3. **Generate environment file** from allocated ports

4. **Docker Compose uses environment file** for port mapping

### Environment File Generation

Create a `.env.docker` file in each worktree with allocated ports:

```bash
# In worktree directory: test-int-api/.env.docker
WEB_PORT=8081
DB_PORT=5433
REDIS_PORT=6380
WORKTREE_ID=test-int-api
```

### Manual Generation

```bash
# Navigate to worktree
cd ../test-int-api

# Create environment file manually
cat > .env.docker << EOF
WEB_PORT=8081
DB_PORT=5433
REDIS_PORT=6380
WORKTREE_ID=test-int-api
EOF
```

### Automated Generation

Add to `worktree_create.py` script:

```python
def generate_docker_env(worktree_path, worktree_name, ports):
    """Generate .env.docker file with allocated ports."""
    env_file = worktree_path / ".env.docker"

    with open(env_file, 'w') as f:
        f.write(f"WEB_PORT={ports['web']}\n")
        f.write(f"DB_PORT={ports['db']}\n")
        f.write(f"REDIS_PORT={ports['redis']}\n")
        f.write(f"WORKTREE_ID={worktree_name}\n")

    print(f"Generated {env_file}")
```

### Port Conflict Avoidance

**The system prevents conflicts by:**

1. **Tracking Allocated Ports**: Stores all assigned ports in `allocated_ports.json`
2. **Checking Before Assignment**: Scans for available ports before allocating
3. **Port Ranges**: Uses different ranges for different services
   - Web: 8080-8999
   - Database: 5433-5999
   - Redis: 6380-6999
4. **Cleanup on Removal**: Frees ports when worktree is removed

---

## Workflow Example

Complete step-by-step workflow for creating a worktree with Docker testing.

### Step 1: Create Worktree with Port Allocation

```bash
# Create worktree for integration API testing
python scripts/worktree_create.py \
  --purpose test \
  --identifier int-api \
  --branch feat \
  --ports

# Output:
# Created worktree: test-int-api
# Allocated ports:
#   Web: 8081
#   DB: 5433
#   Redis: 6380
```

### Step 2: Navigate to Worktree

```bash
cd ../test-int-api
```

**Explanation**: Worktrees are created as sibling directories to the main repository. If you're in `/project`, the worktree is at `/test-int-api`.

### Step 3: Generate Docker Environment File

```bash
# Create .env.docker with allocated ports
cat > .env.docker << EOF
WEB_PORT=8081
DB_PORT=5433
REDIS_PORT=6380
WORKTREE_ID=test-int-api
EOF

# Verify contents
cat .env.docker
```

### Step 4: Copy Docker Compose Template

```bash
# Copy template from main repository
cp ../main-repo/docker-compose.worktree.yml ./docker-compose.yml

# Or if template is in worktree already, just use it
```

### Step 5: Start Docker Containers

```bash
# Start all services in background
docker compose -f docker-compose.yml --env-file .env.docker up -d

# Output:
# Creating network "net-test-int-api"
# Creating container db-test-int-api
# Creating container redis-test-int-api
# Creating container app-test-int-api
```

**Command Breakdown:**
- `-f docker-compose.yml`: Specify compose file
- `--env-file .env.docker`: Load environment variables from file
- `up`: Create and start containers
- `-d`: Detached mode (run in background)

### Step 6: Verify Containers Are Running

```bash
# Check container status
docker compose ps

# Expected output:
# NAME                  STATUS    PORTS
# app-test-int-api     running   0.0.0.0:8081->8080/tcp
# db-test-int-api      running   0.0.0.0:5433->5432/tcp
# redis-test-int-api   running   0.0.0.0:6380->6379/tcp
```

### Step 7: Run Database Migrations (if needed)

```bash
# Run migrations inside app container
docker compose exec app python manage.py migrate

# Or connect to database and run SQL
docker compose exec db psql -U postgres -d mydb
```

### Step 8: Run Integration Tests

```bash
# Run pytest inside container
docker compose exec app pytest tests/integration/

# Or run on host (if dependencies installed)
pytest tests/integration/

# Tests will connect to services on allocated ports:
# - API at localhost:8081
# - Database at localhost:5433
# - Redis at localhost:6380
```

### Step 9: View Logs (if tests fail)

```bash
# View all logs
docker compose logs

# View specific service logs
docker compose logs app
docker compose logs db

# Follow logs in real-time
docker compose logs -f app
```

### Step 10: Cleanup When Done

```bash
# Stop and remove containers
docker compose down

# Remove volumes (reset database state)
docker compose down -v

# Navigate back to main repo
cd ../main-repo

# Remove worktree and free ports
python scripts/worktree_remove.py test-int-api

# Output:
# Stopped containers: app-test-int-api, db-test-int-api, redis-test-int-api
# Removed containers: app-test-int-api, db-test-int-api, redis-test-int-api
# Freed ports: 8081, 5433, 6380
# Removed worktree: test-int-api
```

---

## Next Steps

Continue to [Part 2: Best Practices & Troubleshooting](docker-worktree-testing-part2-best-practices.md) for:
- Container naming conventions
- Resource limits per worktree
- Cleanup procedures
- Data persistence strategies
- Network isolation
- Health checks
- Common troubleshooting solutions
