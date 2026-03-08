# Port Management - Part 1: Overview and Registry Structure

## Table of Contents

1. [When you need to understand port management → Overview](#overview)
   - 1.1 [What is a Port?](#what-is-a-port)
   - 1.2 [Why Port Management is Needed](#why-port-management-is-needed)
   - 1.3 [Port Range Organization](#port-range-organization)
2. [If you need to understand the registry format → Port Registry Structure](#port-registry-structure)
   - 2.1 [Registry File Location](#registry-file-location)
   - 2.2 [Full Registry Schema](#full-registry-schema)
   - 2.3 [Registry Schema Fields Explained](#registry-schema-fields-explained)
   - 2.4 [Initializing a New Registry](#initializing-a-new-registry)

**Related Parts:**

- [Part 2: Allocation Functions and CLI](port-management-part2-allocation-cli.md)
- [Part 3: Conflict Detection and Health Checking](port-management-part3-conflicts-health.md)
- [Part 4: Docker Integration](port-management-part4-docker.md)
- [Part 5: Troubleshooting](port-management-part5-troubleshooting.md)

---

## Overview

Port management in Integrator Agent ensures that services running in different worktrees do not conflict by attempting to use the same network port. This reference document explains the complete port allocation system, including registry structure, allocation functions, CLI commands, and conflict resolution strategies.

### What is a Port?

A **port** is a numbered endpoint on a computer where network services listen for connections. Ports range from 1 to 65535. Each service running on your computer must use a unique port number. For example:

- Web servers typically use port 80 (HTTP) or 443 (HTTPS)
- PostgreSQL database typically uses port 5432
- Redis typically uses port 6379

### Why Port Management is Needed

When working with multiple worktrees, each worktree may run the same services (web server, database, API). Without port management:

- All worktrees would try to use the same default ports
- Services would fail to start with "port already in use" errors
- You would need to manually track which port each worktree is using

The AMIA port management system solves this by:

- Automatically allocating unique ports to each worktree
- Tracking all port assignments in a central registry
- Detecting and preventing conflicts before they occur
- Supporting multiple service types with dedicated port ranges

### Port Range Organization

AMIA organizes ports into **service-specific ranges**:

| Service Type | Start Port | End Port | Purpose |
|--------------|-----------|----------|---------|
| Web | 8080 | 8099 | HTTP web servers, frontend development servers |
| Database | 5432 | 5439 | PostgreSQL, MySQL, MongoDB instances |
| Testing | 9000 | 9099 | Test runners, test servers, mock services |
| Debug | 5555 | 5564 | Debugger connections, debugging proxies |
| API | 3000 | 3099 | REST APIs, GraphQL servers, backend services |
| Cache | 6379 | 6389 | Redis, Memcached instances |

This organization prevents mixing incompatible services and makes it easier to identify service types by port number.

---

## Port Registry Structure

The port registry is stored at `design/worktrees/ports.json` relative to your repository root. This file contains all port allocations and range definitions.

### Registry File Location

The registry file is located at:

```
<repository-root>/design/worktrees/ports.json
```

**Example paths:**

- `/home/user/myproject/design/worktrees/ports.json`
- `/Users/developer/repos/api-service/design/worktrees/ports.json`

### Full Registry Schema

```json
{
  "ranges": {
    "web": {
      "start": 8080,
      "end": 8099,
      "description": "HTTP web servers and frontend development servers"
    },
    "database": {
      "start": 5432,
      "end": 5439,
      "description": "Database services (PostgreSQL, MySQL, MongoDB)"
    },
    "testing": {
      "start": 9000,
      "end": 9099,
      "description": "Test runners, test servers, mock services"
    },
    "debug": {
      "start": 5555,
      "end": 5564,
      "description": "Debugger connections and debugging proxies"
    },
    "api": {
      "start": 3000,
      "end": 3099,
      "description": "REST APIs, GraphQL servers, backend services"
    },
    "cache": {
      "start": 6379,
      "end": 6389,
      "description": "Redis, Memcached, and other caching services"
    }
  },
  "allocations": [
    {
      "port": 8080,
      "worktree": "review-GH-42",
      "service": "web",
      "allocated_at": "2025-12-31T10:00:00Z",
      "allocated_by": "user@hostname",
      "description": "Frontend development server for PR #42",
      "process_id": null,
      "health_status": "unknown"
    },
    {
      "port": 5432,
      "worktree": "review-GH-42",
      "service": "database",
      "allocated_at": "2025-12-31T10:01:00Z",
      "allocated_by": "user@hostname",
      "description": "PostgreSQL instance for PR #42 testing",
      "process_id": 12345,
      "health_status": "healthy"
    }
  ],
  "metadata": {
    "version": "1.0.0",
    "last_updated": "2025-12-31T10:01:00Z",
    "total_allocations": 2,
    "schema_version": 1
  }
}
```

### Registry Schema Fields Explained

#### Ranges Section

The `ranges` section defines port ranges for each service type.

**Fields:**

- `start` (integer): First port number in the range (inclusive)
- `end` (integer): Last port number in the range (inclusive)
- `description` (string): Human-readable explanation of what this range is used for

**Example:**

```json
"web": {
  "start": 8080,
  "end": 8099,
  "description": "HTTP web servers and frontend development servers"
}
```

This means ports 8080 through 8099 (20 ports total) are reserved for web services.

#### Allocations Section

The `allocations` section is an array of all currently allocated ports.

**Fields:**

- `port` (integer): The allocated port number
- `worktree` (string): Name of the worktree using this port
- `service` (string): Service type (must match a key in `ranges`)
- `allocated_at` (ISO 8601 timestamp): When the port was allocated
- `allocated_by` (string): Username and hostname that allocated the port
- `description` (string): Human-readable description of what this port is used for
- `process_id` (integer or null): Operating system process ID using this port, or null if not tracked
- `health_status` (string): Health check status - one of: `unknown`, `healthy`, `unhealthy`, `not_running`

**Example:**

```json
{
  "port": 8080,
  "worktree": "review-GH-42",
  "service": "web",
  "allocated_at": "2025-12-31T10:00:00Z",
  "allocated_by": "developer@laptop",
  "description": "Frontend development server for PR #42",
  "process_id": null,
  "health_status": "unknown"
}
```

#### Metadata Section

The `metadata` section contains registry-level information.

**Fields:**

- `version` (string): Registry format version
- `last_updated` (ISO 8601 timestamp): Last time the registry was modified
- `total_allocations` (integer): Count of active port allocations
- `schema_version` (integer): Schema version number for compatibility checking

### Initializing a New Registry

If the registry file does not exist, you must create it with the initial structure:

```bash
# Create the design/worktrees directory
mkdir -p design/worktrees

# Initialize the registry file
cat > design/worktrees/ports.json << 'EOF'
{
  "ranges": {
    "web": {"start": 8080, "end": 8099, "description": "HTTP web servers"},
    "database": {"start": 5432, "end": 5439, "description": "Database services"},
    "testing": {"start": 9000, "end": 9099, "description": "Test servers"},
    "debug": {"start": 5555, "end": 5564, "description": "Debuggers"},
    "api": {"start": 3000, "end": 3099, "description": "API servers"},
    "cache": {"start": 6379, "end": 6389, "description": "Cache services"}
  },
  "allocations": [],
  "metadata": {
    "version": "1.0.0",
    "last_updated": "2025-12-31T00:00:00Z",
    "total_allocations": 0,
    "schema_version": 1
  }
}
EOF
```

---

**Continue to:** [Part 2: Allocation Functions and CLI](port-management-part2-allocation-cli.md)

**Last Updated:** 2025-12-31
