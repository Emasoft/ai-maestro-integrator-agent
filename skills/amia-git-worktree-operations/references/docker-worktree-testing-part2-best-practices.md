# Docker Worktree Testing - Part 2: Best Practices & Troubleshooting

## Table of Contents

1. [If you need implementation guidelines - Best Practices](#best-practices)
   - [When naming containers - Container Naming Conventions](#container-naming-conventions)
   - [If setting resource limits - Resource Limits Per Worktree](#resource-limits-per-worktree)
   - [When cleaning up containers - Cleanup Procedures](#cleanup-procedures)
   - [If managing data persistence - Data Persistence Strategy](#data-persistence-strategy)
   - [When isolating networks - Network Isolation](#network-isolation)
   - [If managing environment files - Environment File Management](#environment-file-management)
   - [When implementing health checks - Health Checks](#health-checks)
2. [If you need advanced techniques - Advanced Patterns](#advanced-patterns)
   - [When you need Docker expertise - Linking to Docker Container Expert Skill](#linking-to-docker-container-expert-skill)
3. [When you encounter Docker problems - Troubleshooting](#troubleshooting)
   - [If port is already in use](#problem-port-already-in-use)
   - [If container name conflicts](#problem-container-name-conflict)
   - [If database connection refused](#problem-database-connection-refused)
   - [If volume permission issues](#problem-volume-permission-issues)
   - [If old data in containers](#problem-old-data-in-containers)
   - [If slow build times](#problem-slow-build-times)
   - [If can't access service from host](#problem-cant-access-service-from-host)
4. [If you need a quick summary - Summary](#summary)

**Related Documentation:**
- [Part 1: Setup & Configuration](docker-worktree-testing-part1-setup.md) - Overview, patterns, Docker Compose, port configuration, workflow example

---

## Best Practices

### Container Naming Conventions

**Always include worktree identifier in container names:**

Good:
- `app-test-int-api`
- `db-hotfix-security`
- `redis-feat-caching`

Bad:
- `app` (conflicts with other worktrees)
- `myapp` (unclear which worktree)
- `container1` (meaningless)

**Benefits:**
- Easy to identify which worktree owns each container
- Prevents name conflicts
- Simplifies cleanup and debugging

### Resource Limits Per Worktree

Prevent worktrees from consuming all system resources by setting limits in Docker Compose:

```yaml
services:
  app:
    # ... other config ...
    deploy:
      resources:
        limits:
          # Maximum 1GB RAM
          memory: 1G
          # Maximum 1 CPU core
          cpus: '1.0'
        reservations:
          # Reserve at least 512MB RAM
          memory: 512M
          # Reserve at least 0.5 CPU core
          cpus: '0.5'
```

**Recommended Limits:**
- **Small worktrees** (unit tests): 512MB RAM, 0.5 CPU
- **Medium worktrees** (integration tests): 1GB RAM, 1 CPU
- **Large worktrees** (performance tests): 2GB RAM, 2 CPU

### Cleanup Procedures

**Always clean up containers when done with worktree:**

```bash
# Stop containers (keeps data)
docker compose stop

# Stop and remove containers (keeps volumes)
docker compose down

# Stop, remove containers AND volumes (complete cleanup)
docker compose down -v

# Remove everything including images
docker compose down -v --rmi all
```

**Automated Cleanup:**

Integrate cleanup into `worktree_remove.py`:

```python
def cleanup_docker(worktree_name):
    """Stop and remove Docker containers for worktree."""
    import subprocess

    # Find containers with worktree name
    result = subprocess.run(
        ['docker', 'ps', '-a', '--filter', f'name={worktree_name}', '--format', '{{.Names}}'],
        capture_output=True,
        text=True
    )

    containers = result.stdout.strip().split('\n')

    for container in containers:
        if container:  # Skip empty lines
            # Stop container
            subprocess.run(['docker', 'stop', container])
            # Remove container
            subprocess.run(['docker', 'rm', container])

    print(f"Cleaned up containers for: {worktree_name}")
```

### Data Persistence Strategy

**Choose based on testing needs:**

1. **Ephemeral Data** (default for testing):
   ```yaml
   volumes:
     # Anonymous volume - deleted with container
     - /var/lib/postgresql/data
   ```

2. **Persistent Data** (keep between test runs):
   ```yaml
   volumes:
     # Named volume - survives container removal
     - db-data-${WORKTREE_ID}:/var/lib/postgresql/data
   ```

3. **Host-Mounted Data** (direct access from host):
   ```yaml
   volumes:
     # Mount host directory
     - ./data:/var/lib/postgresql/data
   ```

**Recommendation**: Use ephemeral data for most tests, persistent data for debugging.

### Network Isolation

**Each worktree should have isolated network:**

```yaml
networks:
  worktree-net:
    name: net-${WORKTREE_ID}
    driver: bridge
```

**Benefits:**
- Containers in different worktrees can't communicate
- Prevents cross-contamination of test data
- Allows same internal hostnames across worktrees

### Environment File Management

**Never commit `.env.docker` files:**

Add to `.gitignore`:
```
.env.docker
.env.*.docker
```

**Generate dynamically** from allocated ports instead.

### Health Checks

Add health checks to ensure services are ready before tests:

```yaml
services:
  db:
    # ... other config ...
    healthcheck:
      # Check if PostgreSQL is accepting connections
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      # Check every 5 seconds
      interval: 5s
      # Wait up to 5 seconds for response
      timeout: 5s
      # Retry 5 times before marking unhealthy
      retries: 5
      # Wait 10 seconds before first check
      start_period: 10s

  redis:
    # ... other config ...
    healthcheck:
      # Check if Redis responds to PING
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5
```

**Wait for health before running tests:**

```bash
# Wait for all services to be healthy
docker compose up -d --wait

# Now run tests
pytest tests/integration/
```

---

## Advanced Patterns

### Linking to Docker Container Expert Skill

For advanced Docker patterns and optimization, see the **docker-container-expert** skill which covers:

- **Multi-stage builds** for smaller images
- **Build caching** strategies for faster builds
- **Layer optimization** to reduce image size
- **Security scanning** with Trivy and Grype
- **Resource monitoring** and profiling
- **Network debugging** between containers
- **Volume backup and restore** procedures

Read the `docker-container-expert` skill for:
- Complex multi-container orchestration
- Production-like testing environments
- Container debugging techniques
- Performance optimization
- Security hardening

---

## Troubleshooting

### Problem: Port Already in Use

**Symptoms:**
```
Error: bind: address already in use
```

**Solution:**
1. Check what's using the port:
   ```bash
   lsof -i :8081
   # Or on Linux:
   netstat -tulpn | grep 8081
   ```

2. Either stop the process or allocate different port:
   ```bash
   # Update .env.docker
   WEB_PORT=8082  # Use different port
   ```

3. Restart containers:
   ```bash
   docker compose down
   docker compose up -d
   ```

### Problem: Container Name Conflict

**Symptoms:**
```
Error: container name already in use
```

**Solution:**
1. Check existing containers:
   ```bash
   docker ps -a | grep test-int-api
   ```

2. Remove old containers:
   ```bash
   docker rm -f app-test-int-api
   # Or remove all for worktree:
   docker rm -f $(docker ps -a --filter name=test-int-api --format {{.Names}})
   ```

3. Ensure `WORKTREE_ID` is unique in `.env.docker`

### Problem: Database Connection Refused

**Symptoms:**
- Tests fail with "connection refused"
- Can't connect to database on allocated port

**Solution:**
1. Check if database container is running:
   ```bash
   docker compose ps db
   ```

2. Check database logs:
   ```bash
   docker compose logs db
   ```

3. Wait for database to be ready:
   ```bash
   # Use health check
   docker compose up -d --wait

   # Or wait manually
   until docker compose exec db pg_isready; do sleep 1; done
   ```

4. Verify port mapping:
   ```bash
   docker compose port db 5432
   # Should show: 0.0.0.0:5433
   ```

### Problem: Volume Permission Issues

**Symptoms:**
```
Error: permission denied
mkdir: cannot create directory: Permission denied
```

**Solution:**
1. Run container with matching user ID:
   ```yaml
   services:
     app:
       user: "${UID}:${GID}"
   ```

2. Set in `.env.docker`:
   ```bash
   UID=$(id -u)
   GID=$(id -g)
   ```

3. Or fix permissions in Dockerfile:
   ```dockerfile
   RUN chown -R appuser:appuser /app
   USER appuser
   ```

### Problem: Old Data in Containers

**Symptoms:**
- Tests pass locally but fail in worktree
- Database has unexpected data

**Solution:**
1. Complete cleanup:
   ```bash
   docker compose down -v  # Remove volumes
   ```

2. Rebuild images:
   ```bash
   docker compose build --no-cache
   docker compose up -d
   ```

3. Run migrations again:
   ```bash
   docker compose exec app python manage.py migrate
   ```

### Problem: Slow Build Times

**Symptoms:**
- `docker compose up` takes minutes
- Building on every code change

**Solution:**
1. Use volume mounts (already in template):
   ```yaml
   volumes:
     - .:/app  # Changes reflected immediately
   ```

2. Add `.dockerignore`:
   ```
   .git
   .venv
   __pycache__
   *.pyc
   node_modules
   ```

3. Use BuildKit:
   ```bash
   DOCKER_BUILDKIT=1 docker compose build
   ```

### Problem: Can't Access Service from Host

**Symptoms:**
- `curl localhost:8081` fails
- Browser can't connect to app

**Solution:**
1. Verify port mapping:
   ```bash
   docker compose ps
   # Check PORTS column
   ```

2. Check container is listening on 0.0.0.0, not 127.0.0.1:
   ```yaml
   # In app code:
   app.run(host='0.0.0.0', port=8080)  # Good
   app.run(host='127.0.0.1', port=8080)  # Bad
   ```

3. Check firewall rules

4. Test from inside container:
   ```bash
   docker compose exec app curl localhost:8080
   ```

---

## Summary

Docker worktree testing provides:
- **Isolated environments** for each branch/worktree
- **Parallel testing** without conflicts
- **Reproducible setups** across team
- **Clean state** for each test run

**Key points:**
1. Use unique ports per worktree
2. Include worktree ID in container names
3. Generate `.env.docker` from allocated ports
4. Clean up containers when removing worktree
5. Use health checks before running tests

**See Also:**
- [Part 1: Setup & Configuration](docker-worktree-testing-part1-setup.md) - Patterns, templates, workflow
- `worktree-creation.md` - Creating worktrees
- `port-allocation.md` - Port management system
- `worktree-removal.md` - Cleanup procedures
- `docker-container-expert` skill - Advanced Docker patterns
