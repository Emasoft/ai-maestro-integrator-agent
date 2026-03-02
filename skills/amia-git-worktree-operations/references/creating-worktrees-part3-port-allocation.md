# Creating Worktrees: Port Allocation Strategy

## Overview

This document covers when and how to allocate ports for worktrees that run services.

## Table of Contents

1. [When to Allocate Ports](#when-to-allocate-ports)
2. [Port Allocation Process](#port-allocation-process)
3. [Port Ranges and Conventions](#port-ranges-and-conventions)

---

## When to Allocate Ports

**Allocate ports when**:
- Worktree will run web servers (frontend dev servers)
- Worktree will run API servers (backend services)
- Worktree will run databases (PostgreSQL, MySQL, MongoDB, etc.)
- Worktree will run other services (Redis, Elasticsearch, etc.)
- Multiple services need to run simultaneously in one worktree

**Do NOT allocate ports when**:
- Worktree is for code review only (reading code, no execution)
- Worktree is for documentation changes
- Worktree is for quick bug fixes that don't require running services
- Worktree will only run tests (tests can use dynamic/random ports)

---

## Port Allocation Process

### STEP 1: Determine port requirements

Identify how many ports the worktree needs:
- Web frontend: 1 port
- API backend: 1 port
- Database: 1 port per database service
- Cache (Redis/Memcached): 1 port
- WebSocket server: 1 port
- Additional services: 1 port each

**Example**: A full-stack app might need:
- Port 1: Frontend dev server (React, Vue, etc.)
- Port 2: Backend API (Express, Django, etc.)
- Port 3: PostgreSQL database
- Port 4: Redis cache

### STEP 2: Check available ports

Query the registry to find available ports:
```bash
# List all allocated ports
jq -r '.worktrees[].ports[]' .worktree-registry.json | sort -n

# Find next available port starting from 3000
next_port=3000
while jq -e --arg port "$next_port" '.worktrees[].ports[] | select(. == ($port | tonumber))' .worktree-registry.json > /dev/null; do
  ((next_port++))
done
echo "Next available port: $next_port"
```

### STEP 3: Reserve ports in registry

Add ports to the registry entry when creating the worktree:
```json
{
  "name": "feature-user-profiles",
  "ports": [3002, 3003, 5433, 6380]
}
```

**What each port means in this example**:
- 3002: Frontend dev server
- 3003: Backend API server
- 5433: PostgreSQL database
- 6380: Redis cache

### STEP 4: Configure services to use allocated ports

Update configuration files in the worktree:

**.env file**:
```bash
# Frontend
PORT=3002
VITE_PORT=3002  # If using Vite

# Backend
API_PORT=3003
SERVER_PORT=3003

# Database
DATABASE_PORT=5433
POSTGRES_PORT=5433

# Cache
REDIS_PORT=6380
```

**package.json scripts** (for Node.js projects):
```json
{
  "scripts": {
    "dev": "PORT=3002 vite",
    "api": "PORT=3003 node server.js"
  }
}
```

**Docker Compose** (if using Docker):
```yaml
services:
  frontend:
    ports:
      - "3002:3000"

  backend:
    ports:
      - "3003:3000"

  database:
    ports:
      - "5433:5432"

  redis:
    ports:
      - "6380:6379"
```

---

## Port Ranges and Conventions

**Standard port ranges**:
- 3000-3099: Web frontend servers
- 3100-3199: Backend API servers
- 5400-5499: PostgreSQL databases
- 6300-6399: Redis instances
- 9200-9299: Elasticsearch instances
- 27000-27099: MongoDB instances

**Why use ranges**: Organizing ports by service type makes troubleshooting easier and prevents conflicts.

**Example allocation**:
```
Main repo:
  Frontend: 3000
  API: 3100
  PostgreSQL: 5432
  Redis: 6379

review-GH-42:
  Frontend: 3001
  API: 3101
  PostgreSQL: 5433
  Redis: 6380

feature-user-profiles:
  Frontend: 3002
  API: 3102
  PostgreSQL: 5434
  Redis: 6381
```

---

## Related Documentation

- [Standard Creation Flow](./creating-worktrees-part1-standard-flow.md)
- [Purpose-Specific Patterns](./creating-worktrees-part2-purpose-patterns.md)
- [Environment Setup](./creating-worktrees-part4-environment-setup.md)
- [Commands Reference and Checklist](./creating-worktrees-part5-commands-checklist.md)
- [Troubleshooting](./creating-worktrees-part6-troubleshooting.md)
