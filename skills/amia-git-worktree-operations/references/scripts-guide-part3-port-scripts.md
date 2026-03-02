# Worktree Automation Scripts Guide - Part 3: Port Scripts

**Related Documents:**
- [Main Index](scripts-guide.md)
- [Part 1: Core Scripts](scripts-guide-part1-core-scripts.md)
- [Part 2: Management Scripts](scripts-guide-part2-management-scripts.md)
- [Part 4: Common Workflows](scripts-guide-part4-workflows.md)
- [Part 5: Troubleshooting](scripts-guide-part5-troubleshooting.md)

---

## Table of Contents

- [Script Reference: Port Scripts](#script-reference-port-scripts)
  - [port_allocate.py](#port_allocatepy)
    - [Purpose](#purpose)
    - [Usage Syntax](#usage-syntax)
    - [Required Arguments (one of)](#required-arguments-one-of)
    - [Optional Arguments](#optional-arguments)
    - [Examples with Explanations](#examples-with-explanations)
    - [Port Ranges by Service](#port-ranges-by-service)
    - [Exit Codes](#exit-codes)
  - [port_status.py](#port_statuspy)
    - [Purpose](#purpose-1)
    - [Usage Syntax](#usage-syntax-1)
    - [Optional Arguments](#optional-arguments-1)
    - [Examples with Explanations](#examples-with-explanations-1)
    - [Health Check Behavior](#health-check-behavior)
    - [Exit Codes](#exit-codes-1)

---

## Script Reference: Port Scripts

This section covers port management scripts:
- **port_allocate.py** - Allocate and release ports for services
- **port_status.py** - Display port allocation status and health checks

---

### port_allocate.py

#### Purpose

Manually allocates development server ports to worktrees or releases them back to the pool.

#### Usage Syntax

```bash
python scripts/port_allocate.py [OPTIONS]
```

#### Required Arguments (one of)

- **--service** - Service name to allocate port for
  - Valid values: `web`, `api`, `db`, `redis`, `grpc`, `websocket`
  - Must be combined with --worktree

- **--release** - Port number to release back to pool
  - Must be currently allocated
  - Releases port from its worktree
  - Example: `--release 8001`

- **--check** - Check if a specific port is available
  - Does not allocate, only queries
  - Example: `--check 8001`

- **--available** - List all available ports for a service
  - Must be combined with service name
  - Example: `--available web`

#### Optional Arguments

- **--worktree** - Worktree name to allocate port to
  - Required with --service
  - Must be a registered worktree
  - Example: `--worktree review-GH-42`

#### Examples with Explanations

**Example 1: Allocate web server port to worktree**

```bash
python scripts/port_allocate.py --service web --worktree review-GH-42
```

**Output:**
```
Allocating port for service 'web' to worktree 'review-GH-42'

Searching for available port in range: 8000-8099
Port 8000: In use by feature-auth-system
Port 8001: In use by bugfix-memory-leak
Port 8002: Available

✓ Allocated port 8002 for service 'web'
✓ Updated registry for worktree 'review-GH-42'

Configuration:
  Worktree: review-GH-42
  Service: web
  Port: 8002

To start service, run in worktree directory:
  npm run dev -- --port 8002
```

**When to use:** Worktree was created without --ports flag, now needs a development server.

---

**Example 2: Release allocated port**

```bash
python scripts/port_allocate.py --release 8002
```

**Output:**
```
Releasing port 8002

Port 8002 is currently allocated to:
  Worktree: review-GH-42
  Service: web
  Allocated at: 2024-01-15T10:30:00

✓ Port 8002 released
✓ Updated registry for worktree 'review-GH-42'

Port 8002 is now available for allocation.
```

**When to use:** Service is no longer needed, freeing port for other worktrees.

---

**Example 3: Check if specific port is available**

```bash
python scripts/port_allocate.py --check 8005
```

**Output:**
```
Checking port 8005 availability

Port 8005: AVAILABLE
- Not allocated to any worktree
- Valid for services: web (8000-8099)

This port can be allocated immediately.
```

**When to use:** Before manually configuring service to use specific port.

---

**Example 4: List all available ports for a service**

```bash
python scripts/port_allocate.py --available web
```

**Output:**
```
Available ports for service 'web' (range: 8000-8099)

Currently allocated (7 ports):
  8000 → feature-auth-system
  8001 → bugfix-memory-leak
  8002 → review-GH-42
  8003 → experiment-async
  8010 → refactor-database
  8020 → hotfix-security
  8050 → docs-update

Available ports (93 remaining):
  8004-8009, 8011-8019, 8021-8049, 8051-8099

Next suggested port: 8004
```

**When to use:** Planning port allocation or checking capacity.

---

**Example 5: Allocate multiple services to same worktree**

```bash
# Allocate web server
python scripts/port_allocate.py --service web --worktree feature-fullstack

# Allocate API server
python scripts/port_allocate.py --service api --worktree feature-fullstack

# Allocate database
python scripts/port_allocate.py --service db --worktree feature-fullstack
```

**Output (cumulative):**
```
After all three commands:

Worktree 'feature-fullstack' now has:
  web: 8001
  api: 9001
  db: 5433

Registry entry:
{
  "ports": {
    "web": 8001,
    "api": 9001,
    "db": 5433
  }
}
```

**When to use:** Full-stack development requiring multiple simultaneous services.

---

#### Port Ranges by Service

| Service     | Range        | Default Start |
|-------------|--------------|---------------|
| web         | 8000-8099    | 8000          |
| api         | 9000-9099    | 9000          |
| db          | 5432-5532    | 5432          |
| redis       | 6379-6479    | 6379          |
| grpc        | 50051-50151  | 50051         |
| websocket   | 3000-3099    | 3000          |

#### Exit Codes

- **0** - Success, operation completed
- **1** - Invalid arguments or missing required parameters
- **2** - Worktree not found in registry
- **3** - No ports available in range
- **4** - Port already allocated (when checking specific port)
- **5** - Registry file is corrupted or unwritable

---

### port_status.py

#### Purpose

Displays current port allocation status with optional health checks to verify services are actually running.

#### Usage Syntax

```bash
python scripts/port_status.py [OPTIONS]
```

#### Optional Arguments

- **--all** - Show all port allocations (default behavior)
  - Displays every allocated port across all worktrees
  - Organized by worktree name

- **--worktree** - Show ports for specific worktree only
  - Example: `--worktree review-GH-42`
  - Shows only ports allocated to that worktree

- **--service** - Show allocations for specific service type
  - Example: `--service web`
  - Shows all worktrees using that service type

- **--health-check** - Test if services are actually responding
  - Attempts TCP connection to each port
  - Reports running/stopped status
  - Timeout: 2 seconds per port

- **--json** - Output in JSON format
  - Useful for scripting and monitoring
  - Includes health check results if requested

#### Examples with Explanations

**Example 1: Show all port allocations (default)**

```bash
python scripts/port_status.py --all
```

**Output:**
```
Port Allocation Status
======================

review-GH-42:
  web:       8002
  api:       9002

feature-auth-system:
  web:       8001
  api:       9001
  db:        5433

bugfix-memory-leak:
  web:       8003

Total allocations: 6 ports across 3 worktrees
Available capacity:
  web: 96/100 ports free
  api: 97/100 ports free
  db:  99/100 ports free
```

**When to use:** Quick overview of all port assignments.

---

**Example 2: Show ports for specific worktree**

```bash
python scripts/port_status.py --worktree feature-auth-system
```

**Output:**
```
Port Status for Worktree: feature-auth-system
==============================================

Allocated Ports:
  web:       8001
  api:       9001
  db:        5433

Allocation Details:
  Service: web
    Port: 8001
    Allocated: 2024-01-15T10:30:00 (2 days ago)
    Range: 8000-8099

  Service: api
    Port: 9001
    Allocated: 2024-01-15T10:30:00 (2 days ago)
    Range: 9000-9099

  Service: db
    Port: 5433
    Allocated: 2024-01-15T10:31:00 (2 days ago)
    Range: 5432-5532
```

**When to use:** Checking port configuration for specific worktree before starting services.

---

**Example 3: Health check all allocated ports**

```bash
python scripts/port_status.py --all --health-check
```

**Output:**
```
Port Allocation Status with Health Check
=========================================

review-GH-42:
  web:       8002    [RUNNING]  ✓
  api:       9002    [STOPPED]  ✗

feature-auth-system:
  web:       8001    [RUNNING]  ✓
  api:       9001    [RUNNING]  ✓
  db:        5433    [RUNNING]  ✓

bugfix-memory-leak:
  web:       8003    [STOPPED]  ✗

Health Summary:
  Running:  4 services
  Stopped:  2 services
  Errors:   0 services

Note: STOPPED status means port is allocated but no service is responding.
      This is normal if you haven't started the development server yet.
```

**When to use:** Verifying which services are actually running vs just allocated.

---

**Example 4: Check specific service type across all worktrees**

```bash
python scripts/port_status.py --service web
```

**Output:**
```
Port Status for Service: web
=============================

Allocated Ports (range 8000-8099):

  8001 → feature-auth-system
         Branch: feature/authentication
         Created: 2024-01-15T10:30:00 (2 days ago)

  8002 → review-GH-42
         Branch: feature/auth
         Created: 2024-01-15T11:00:00 (2 days ago)

  8003 → bugfix-memory-leak
         Branch: bugfix/memory-leak
         Created: 2024-01-16T09:15:00 (1 day ago)

Service 'web' usage:
  Allocated: 3 ports
  Available: 97 ports
  Utilization: 3%
```

**When to use:** Finding port conflicts or planning capacity for new worktrees.

---

**Example 5: JSON output with health checks for monitoring**

```bash
python scripts/port_status.py --all --health-check --json
```

**Output:**
```json
{
  "timestamp": "2024-01-17T14:30:00Z",
  "total_allocations": 6,
  "worktrees": [
    {
      "name": "review-GH-42",
      "ports": {
        "web": {
          "port": 8002,
          "allocated_at": "2024-01-15T10:30:00Z",
          "health": "running",
          "response_time_ms": 45
        },
        "api": {
          "port": 9002,
          "allocated_at": "2024-01-15T10:30:00Z",
          "health": "stopped",
          "error": "Connection refused"
        }
      }
    },
    {
      "name": "feature-auth-system",
      "ports": {
        "web": {
          "port": 8001,
          "allocated_at": "2024-01-15T10:30:00Z",
          "health": "running",
          "response_time_ms": 32
        },
        "api": {
          "port": 9001,
          "allocated_at": "2024-01-15T10:30:00Z",
          "health": "running",
          "response_time_ms": 28
        },
        "db": {
          "port": 5433,
          "allocated_at": "2024-01-15T10:31:00Z",
          "health": "running",
          "response_time_ms": 12
        }
      }
    }
  ],
  "summary": {
    "running": 4,
    "stopped": 2,
    "errors": 0
  }
}
```

**When to use:** Integration with monitoring dashboards or CI/CD health checks.

---

#### Health Check Behavior

**What the health check does:**
1. Attempts TCP connection to each allocated port
2. Waits up to 2 seconds for connection
3. Reports status: running, stopped, or error

**Status meanings:**
- **RUNNING** - Service is accepting connections on this port
- **STOPPED** - Port is allocated but nothing is listening
- **ERROR** - Network error or port is blocked

**Important:** Health check only tests TCP connectivity, not HTTP/API functionality.

#### Exit Codes

- **0** - Success, status displayed
- **1** - Invalid arguments
- **2** - Registry file not found or unreadable
- **3** - Worktree specified with --worktree not found
- **4** - Health check encountered errors

---

**End of Part 3: Port Scripts**

**Next:** [Part 4: Common Workflows](scripts-guide-part4-workflows.md) - Step-by-step workflow examples
