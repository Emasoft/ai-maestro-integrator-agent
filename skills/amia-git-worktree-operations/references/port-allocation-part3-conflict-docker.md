# Port Allocation: Conflict Resolution & Docker Integration

## Table of Contents

1. [If you encounter port conflicts → Conflict Resolution](#conflict-resolution)
2. [When you need to use Docker with worktrees → Integration with Docker](#integration-with-docker)

---

## Conflict Resolution

### Types of Conflicts

#### 1. Port Already in Use by System

**Problem:**
```bash
ERROR: Port 8080 is already in use by another process
```

**How to detect:**
```bash
# Check what's using the port
lsof -i :8080
# or on some systems
netstat -an | grep 8080
```

**Solution:**
```bash
# Option 1: Stop the conflicting process
kill <PID>

# Option 2: Skip the port in registry
eia port mark-unavailable 8080 "Used by system service"

# Option 3: Change port ranges
eia port config --web-range 8100-8199
```

#### 2. Registry Out of Sync

**Problem:**
Registry says port is free, but it's actually in use.

**Symptoms:**
```bash
$ eia worktree create feature-new
Allocated port 8081
ERROR: Port 8081 already in use
```

**Solution:**
```bash
# Scan all ports and rebuild registry
eia port scan-rebuild

# This will:
# 1. Check which ports are actually listening
# 2. Match them to worktrees
# 3. Update registry to reflect reality
```

#### 3. Port Range Exhausted

**Problem:**
```bash
ERROR: No available ports in web range (8080-8099)
```

**Solution:**
```bash
# Option 1: Expand the range
eia port config --web-range 8080-8199

# Option 2: Remove unused worktrees
eia worktree list --unused
eia worktree remove old-feature-1

# Option 3: Compact port assignments
eia port compact
# This reassigns ports to fill gaps
```

#### 4. Stale Port Allocations

**Problem:**
Worktree was deleted manually (not via eia), ports still marked as used.

**Solution:**
```bash
# List all allocated ports
eia port list

# Check if worktree still exists
eia worktree list

# Release ports for non-existent worktree
eia port release deleted-worktree-name

# Or run cleanup to auto-detect
eia port cleanup
```

### Automatic Conflict Resolution

**Enable auto-resolution:**
```bash
# In .git/worktree-registry/config.json
{
  "port_conflict_resolution": {
    "auto_resolve": true,
    "strategies": [
      "skip_to_next",      // Try next port in range
      "expand_range",      // Expand range if exhausted
      "force_release"      // Release if worktree gone
    ]
  }
}
```

---

## Integration with Docker

### Why Docker Needs Port Mapping

When running services in Docker containers, you need to map container ports to host ports. Each worktree's containers must use unique host ports.

### Docker Compose Template

**File: `docker-compose.worktree.template.yml`**
```yaml
version: '3.8'

services:
  web:
    image: myapp-web
    ports:
      - "${ALLOCATED_WEB_PORT}:80"
    environment:
      - NODE_ENV=development
      - WORKTREE=${WORKTREE_NAME}
    networks:
      - worktree-network

  db:
    image: postgres:15
    ports:
      - "${ALLOCATED_DB_PORT}:5432"
    environment:
      - POSTGRES_DB=myapp_${WORKTREE_NAME}
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    volumes:
      - db-data:/var/lib/postgresql/data
    networks:
      - worktree-network

  test:
    image: myapp-test
    ports:
      - "${ALLOCATED_TEST_PORT}:3000"
    depends_on:
      - db
    networks:
      - worktree-network

networks:
  worktree-network:
    name: ${WORKTREE_NAME}-network

volumes:
  db-data:
    name: ${WORKTREE_NAME}-db-data
```

### Generating Docker Compose File

```python
def generate_docker_compose(worktree_name):
    """
    Generate docker-compose.yml with allocated ports.
    """
    registry = load_registry()
    ports = registry["allocated_ports"][worktree_name]

    # Load template
    with open('docker-compose.worktree.template.yml', 'r') as f:
        template = f.read()

    # Replace placeholders
    compose = template.replace('${ALLOCATED_WEB_PORT}', str(ports['web']))
    compose = compose.replace('${ALLOCATED_DB_PORT}', str(ports['db']))
    compose = compose.replace('${ALLOCATED_TEST_PORT}', str(ports['test']))
    compose = compose.replace('${WORKTREE_NAME}', worktree_name)

    # Write to worktree directory
    output_path = f'{worktree_name}/docker-compose.yml'
    with open(output_path, 'w') as f:
        f.write(compose)

    print(f"Generated: {output_path}")
    return output_path
```

### Starting Docker Services

```bash
# In worktree directory
cd feature-payment

# Start services with allocated ports
docker-compose up -d

# Check running containers
docker-compose ps

# Output:
# Name                    Port                 State
# feature-payment-web     8082->80/tcp         Up
# feature-payment-db      5434->5432/tcp       Up
# feature-payment-test    9002->3000/tcp       Up
```

### Multiple Worktrees Running Simultaneously

```bash
# Terminal 1: Main worktree
cd main
docker-compose up
# Web: http://localhost:8080
# DB: localhost:5432

# Terminal 2: Feature worktree
cd feature-payment
docker-compose up
# Web: http://localhost:8082
# DB: localhost:5434

# No conflicts! Each worktree uses its own ports
```

### Docker Network Isolation

Each worktree gets its own Docker network to prevent container name conflicts:

```yaml
# feature-payment uses:
networks:
  worktree-network:
    name: feature-payment-network

# feature-login uses:
networks:
  worktree-network:
    name: feature-login-network
```

---

## Related Documents

- [Core Concepts](port-allocation-part1-core-concepts.md) - Why ports matter and allocation algorithm
- [Configuration & Status](port-allocation-part2-config-status.md) - How to generate configs and check port status
- [Cleanup & Troubleshooting](port-allocation-part4-cleanup-troubleshooting.md) - Port cleanup and problem solving
