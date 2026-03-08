# Port Management - Part 3: Conflict Detection and Health Checking

## Table of Contents

1. [When you encounter port conflicts → Conflict Detection](#conflict-detection)
   - 1.1 [What is a Port Conflict?](#what-is-a-port-conflict)
   - 1.2 [Types of Conflicts](#types-of-conflicts)
   - 1.3 [Automated Conflict Detection](#automated-conflict-detection)
2. [If you need to verify services are running → Health Checking](#health-checking)
   - 2.1 [What is a Health Check?](#what-is-a-health-check)
   - 2.2 [Health Check Levels](#health-check-levels)
   - 2.3 [Health Status Values](#health-status-values)
   - 2.4 [Running Health Checks](#running-health-checks)
   - 2.5 [Automated Health Monitoring](#automated-health-monitoring)

**Related Parts:**

- [Part 1: Overview and Registry Structure](port-management-part1-overview-registry.md)
- [Part 2: Allocation Functions and CLI](port-management-part2-allocation-cli.md)
- [Part 4: Docker Integration](port-management-part4-docker.md)
- [Part 5: Troubleshooting](port-management-part5-troubleshooting.md)

---

## Conflict Detection

Conflict detection prevents multiple services from using the same port.

### What is a Port Conflict?

A **port conflict** occurs when:

1. Two allocations in the registry claim the same port number
2. A service tries to use a port already allocated to another worktree
3. A service tries to use a port already in use by a non-worktree process

### Types of Conflicts

#### Type 1: Registry Conflict

**Description:** Two entries in the allocations array have the same port number.

**Cause:** Registry corruption or manual editing errors.

**Detection:**

```python
def detect_registry_conflicts(registry: Dict) -> List[int]:
    """Find duplicate port allocations in registry."""
    ports = [alloc['port'] for alloc in registry['allocations']]
    duplicates = [port for port in ports if ports.count(port) > 1]
    return list(set(duplicates))
```

**Example:**

```json
{
  "allocations": [
    {"port": 8080, "worktree": "review-GH-42", "service": "web"},
    {"port": 8080, "worktree": "feature-search", "service": "web"}
  ]
}
```

This is a conflict: port 8080 is allocated twice.

**Resolution:**

1. Identify which allocation is incorrect (usually the older one)
2. Release one of the conflicting allocations
3. Allocate a new port to the affected worktree

#### Type 2: System Conflict

**Description:** Registry shows a port as available, but the operating system reports it as in use.

**Cause:** A process outside the worktree system is using the port.

**Detection:**

```python
import socket

def detect_system_conflict(port: int) -> bool:
    """Check if port is in use on the system."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('127.0.0.1', port))
        sock.close()
        return False  # No conflict
    except OSError:
        return True  # Conflict detected
```

**Example:**
If port 8080 is free in the registry but `detect_system_conflict(8080)` returns `True`, there's a system conflict.

**Resolution:**

1. Identify the process using the port: `lsof -i :8080` (macOS/Linux) or `netstat -ano | findstr :8080` (Windows)
2. Stop the conflicting process if safe to do so
3. Or allocate a different port to the worktree

#### Type 3: Allocation Mismatch

**Description:** Registry shows a port as allocated, but no process is using it.

**Cause:** Service crashed or was stopped without releasing the port.

**Detection:**

```python
def detect_allocation_mismatch(registry: Dict) -> List[Dict]:
    """Find allocations where no process is using the port."""
    mismatches = []
    for alloc in registry['allocations']:
        if not detect_system_conflict(alloc['port']):
            mismatches.append(alloc)
    return mismatches
```

**Resolution:**

1. Update the allocation's `health_status` to `not_running`
2. Either restart the service or release the port

### Automated Conflict Detection

**Script:** `scripts/port_status.py --check-conflicts`

**Usage:**

```bash
python scripts/port_status.py --check-conflicts
```

**Output:**

```
Port Conflict Detection
=======================

REGISTRY CONFLICT:
  Port 8080 is allocated to multiple worktrees:
    - review-GH-42 (allocated: 2025-12-31 10:00:00)
    - feature-search (allocated: 2025-12-31 11:00:00)

  Resolution: Run 'python scripts/port_allocate.py --release 8080 --worktree feature-search'

SYSTEM CONFLICT:
  Port 5432 is allocated to review-GH-42 but in use by PID 99999 (postgres)

  Resolution: Check if process 99999 is legitimate:
    lsof -i :5432

ALLOCATION MISMATCH:
  Port 9000 is allocated to feature-search but not in use

  Action: Service may have crashed. Check logs or release port:
    python scripts/port_allocate.py --release 9000

Summary:
  Total conflicts: 2
  Total mismatches: 1
```

**When to Run:**

- Before allocating ports
- After system restarts
- When services fail to start
- As part of regular maintenance (weekly)

---

## Health Checking

Health checking verifies that allocated ports are actually free and services are running correctly.

### What is a Health Check?

A **health check** is a test to verify that:

1. A port is free on the operating system
2. A service using an allocated port is running
3. A service is responding to requests on its port

### Health Check Levels

#### Level 1: Port Availability Check

**Purpose:** Verify a port is free at the operating system level.

**Method:** Attempt to bind a socket to the port.

**Implementation:**

```python
import socket

def check_port_free(port: int) -> bool:
    """Check if port is free by attempting to bind to it."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('127.0.0.1', port))
        sock.close()
        return True
    except OSError:
        return False
```

**When to Use:**

- Before allocating a port
- During conflict detection
- After service shutdown

#### Level 2: Process Listening Check

**Purpose:** Verify a process is listening on the port.

**Method:** Check for active network connections on the port.

**Implementation (macOS/Linux):**

```python
import subprocess

def check_port_listening(port: int) -> bool:
    """Check if a process is listening on the port."""
    try:
        result = subprocess.run(
            ['lsof', '-i', f':{port}', '-t'],
            capture_output=True,
            text=True,
            check=False
        )
        return bool(result.stdout.strip())
    except Exception:
        return False
```

**Implementation (Windows):**

```python
import subprocess

def check_port_listening(port: int) -> bool:
    """Check if a process is listening on the port (Windows)."""
    try:
        result = subprocess.run(
            ['netstat', '-ano'],
            capture_output=True,
            text=True,
            check=False
        )
        return f':{port}' in result.stdout
    except Exception:
        return False
```

**When to Use:**

- After starting a service
- During status checks
- Before stopping a service

#### Level 3: Service Response Check

**Purpose:** Verify the service is responding to requests.

**Method:** Send an HTTP request or service-specific ping.

**Implementation (HTTP services):**

```python
import urllib.request

def check_service_responding(port: int, path: str = '/') -> bool:
    """Check if HTTP service is responding on the port."""
    try:
        url = f'http://localhost:{port}{path}'
        with urllib.request.urlopen(url, timeout=5) as response:
            return response.status == 200
    except Exception:
        return False
```

**Implementation (Database services):**

```python
import psycopg2

def check_postgres_responding(port: int) -> bool:
    """Check if PostgreSQL is responding on the port."""
    try:
        conn = psycopg2.connect(
            host='localhost',
            port=port,
            user='postgres',
            database='postgres',
            connect_timeout=5
        )
        conn.close()
        return True
    except Exception:
        return False
```

**When to Use:**

- After starting a service (verify it's working)
- During integration tests
- For monitoring and alerting

### Health Status Values

The registry tracks health status for each allocation:

| Status | Meaning | When Set |
|--------|---------|----------|
| `unknown` | Health has not been checked | Initial allocation |
| `healthy` | Port is allocated, process is listening, service responds | After successful health check |
| `unhealthy` | Port is allocated, process is listening, but service does not respond | After failed response check |
| `not_running` | Port is allocated but no process is listening | After failed listening check |

### Running Health Checks

**Script:** `scripts/port_status.py --health-check`

**Usage:**

```bash
# Check health of all allocated ports
python scripts/port_status.py --health-check

# Check health of a specific worktree's ports
python scripts/port_status.py --health-check --worktree review-GH-42
```

**Output:**

```
Health Check Results
====================

Worktree: review-GH-42
  Port 8080 (web):
    Port is allocated
    Process is listening (PID: 12345)
    Service responds to HTTP GET /
    Status: healthy

  Port 5432 (database):
    Port is allocated
    Process is listening (PID: 67890)
    PostgreSQL accepts connections
    Status: healthy

Worktree: feature-search
  Port 8081 (web):
    Port is allocated
    No process listening
    Status: not_running
    Action: Start the service or release the port

Summary:
  Healthy: 2
  Not running: 1
  Unhealthy: 0
  Unknown: 0
```

**When to Run:**

- After starting services
- Before running tests
- During troubleshooting
- As part of CI/CD pipelines

### Automated Health Monitoring

You can set up automated health monitoring with a cron job or systemd timer.

**Example cron job (run every 15 minutes):**

```bash
# Edit crontab
crontab -e

# Add this line
*/15 * * * * cd /path/to/repo && python scripts/port_status.py --health-check >> logs/health-check.log 2>&1
```

**Example systemd timer:**

Create `/etc/systemd/system/amia-health-check.service`:

```ini
[Unit]
Description=AMIA Port Health Check

[Service]
Type=oneshot
WorkingDirectory=/path/to/repo
ExecStart=/usr/bin/python3 scripts/port_status.py --health-check
```

Create `/etc/systemd/system/amia-health-check.timer`:

```ini
[Unit]
Description=Run AMIA Port Health Check every 15 minutes

[Timer]
OnBootSec=5min
OnUnitActiveSec=15min

[Install]
WantedBy=timers.target
```

Enable the timer:

```bash
sudo systemctl enable amia-health-check.timer
sudo systemctl start amia-health-check.timer
```

---

**Continue to:** [Part 4: Docker Integration](port-management-part4-docker.md)

**Last Updated:** 2025-12-31
