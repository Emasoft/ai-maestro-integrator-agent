# Port Management - Part 2: Allocation Functions and CLI

## Table of Contents

1. [When you need to allocate ports programmatically → Port Allocation Functions](#port-allocation-functions)
   - 1.1 [Function: allocate_port()](#function-allocate_port)
   - 1.2 [Function: release_port()](#function-release_port)
   - 1.3 [Function: check_port_available()](#function-check_port_available)
   - 1.4 [Function: list_allocated_ports()](#function-list_allocated_ports)
2. [If you need to use port management commands → Command-Line Interface](#command-line-interface)
   - 2.1 [Command: Allocate Port](#command-allocate-port)
   - 2.2 [Command: Release Port](#command-release-port)
   - 2.3 [Command: Check Port Status (All Ports)](#command-check-port-status-all-ports)
   - 2.4 [Command: Check Port Status (Specific Worktree)](#command-check-port-status-specific-worktree)
   - 2.5 [Command: Find Next Available Port](#command-find-next-available-port)

**Related Parts:**
- [Part 1: Overview and Registry Structure](port-management-part1-overview-registry.md)
- [Part 3: Conflict Detection and Health Checking](port-management-part3-conflicts-health.md)
- [Part 4: Docker Integration](port-management-part4-docker.md)
- [Part 5: Troubleshooting](port-management-part5-troubleshooting.md)

---

## Port Allocation Functions

These Python functions manage port allocation operations. They are implemented in the `scripts/port_allocate.py` script.

### Function: allocate_port()

**Purpose:** Allocate a port from the specified service range to a worktree.

**Signature:**
```python
def allocate_port(service_type: str, worktree_id: str, description: str = "") -> int:
    """
    Allocate a port for a service in a worktree.

    Args:
        service_type: Type of service (must match a key in ranges: web, database, testing, etc.)
        worktree_id: Unique identifier for the worktree
        description: Optional human-readable description

    Returns:
        int: The allocated port number

    Raises:
        ValueError: If service_type is not valid
        RuntimeError: If no ports are available in the range
        FileNotFoundError: If registry file does not exist
    """
```

**Algorithm:**
1. Load the registry from `design/worktrees/ports.json`
2. Verify `service_type` exists in `ranges`
3. Get the start and end port for the service type
4. Find all currently allocated ports in that range
5. Iterate through the range to find the first unallocated port
6. Create an allocation entry with metadata
7. Add the allocation to the registry
8. Update registry metadata (last_updated, total_allocations)
9. Write the updated registry back to disk
10. Return the allocated port number

**Example Usage:**
```python
from scripts.port_allocate import allocate_port

# Allocate a web server port for worktree 'feature-login'
port = allocate_port(
    service_type="web",
    worktree_id="feature-login",
    description="Development server for login feature"
)
print(f"Allocated port: {port}")  # Output: Allocated port: 8080
```

**Example Output:**
```
Allocating port for service 'web' in worktree 'feature-login'
Found available port: 8080
Updated registry at design/worktrees/ports.json
Allocated port: 8080
```

### Function: release_port()

**Purpose:** Release a previously allocated port, making it available for reuse.

**Signature:**
```python
def release_port(port: int) -> bool:
    """
    Release an allocated port.

    Args:
        port: The port number to release

    Returns:
        bool: True if port was released, False if port was not allocated

    Raises:
        FileNotFoundError: If registry file does not exist
    """
```

**Algorithm:**
1. Load the registry from `design/worktrees/ports.json`
2. Search for the port in the allocations array
3. If found:
   - Remove the allocation entry
   - Update registry metadata (last_updated, total_allocations)
   - Write the updated registry back to disk
   - Return True
4. If not found:
   - Return False (port was not allocated)

**Example Usage:**
```python
from scripts.port_allocate import release_port

# Release port 8080
success = release_port(8080)
if success:
    print("Port 8080 released successfully")
else:
    print("Port 8080 was not allocated")
```

**Example Output:**
```
Releasing port 8080
Port 8080 released successfully
Updated registry at design/worktrees/ports.json
```

### Function: check_port_available()

**Purpose:** Check if a specific port is available for allocation.

**Signature:**
```python
def check_port_available(port: int) -> bool:
    """
    Check if a port is available.

    Args:
        port: The port number to check

    Returns:
        bool: True if port is available, False if allocated or in use
    """
```

**Algorithm:**
1. Load the registry from `design/worktrees/ports.json`
2. Check if the port exists in any allocation entry
3. If found in allocations: Return False
4. If not found in allocations: Check if port is actually free on the system
5. Use system-level check (attempt to bind to the port)
6. Return True if both checks pass, False otherwise

**Example Usage:**
```python
from scripts.port_allocate import check_port_available

# Check if port 8080 is available
if check_port_available(8080):
    print("Port 8080 is available")
else:
    print("Port 8080 is in use or allocated")
```

**System-Level Port Check:**

The function uses a socket binding test:

```python
import socket

def is_port_free_on_system(port: int) -> bool:
    """Test if a port is free by attempting to bind to it."""
    try:
        # Create a TCP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Attempt to bind to the port
        sock.bind(('127.0.0.1', port))
        # Close the socket immediately
        sock.close()
        return True  # Port is free
    except OSError:
        return False  # Port is in use
```

### Function: list_allocated_ports()

**Purpose:** List all ports allocated to a specific worktree.

**Signature:**
```python
def list_allocated_ports(worktree_id: str) -> List[Dict[str, Any]]:
    """
    List all ports allocated to a worktree.

    Args:
        worktree_id: Unique identifier for the worktree

    Returns:
        List of allocation dictionaries for the worktree
    """
```

**Algorithm:**
1. Load the registry from `design/worktrees/ports.json`
2. Filter allocations where `worktree` field matches `worktree_id`
3. Return the filtered list

**Example Usage:**
```python
from scripts.port_allocate import list_allocated_ports

# List all ports for worktree 'review-GH-42'
allocations = list_allocated_ports("review-GH-42")

for alloc in allocations:
    print(f"Port {alloc['port']} ({alloc['service']}): {alloc['description']}")
```

**Example Output:**
```
Port 8080 (web): Frontend development server for PR #42
Port 5432 (database): PostgreSQL instance for PR #42 testing
Port 9000 (testing): Jest test server for PR #42
```

---

## Command-Line Interface

The port management system provides command-line scripts for common operations.

### Command: Allocate Port

**Script:** `scripts/port_allocate.py`

**Purpose:** Allocate a port to a worktree service.

**Usage:**
```bash
python scripts/port_allocate.py --service SERVICE_TYPE --worktree WORKTREE_NAME [--description DESC]
```

**Parameters:**
- `--service SERVICE_TYPE`: Service type (web, database, testing, debug, api, cache)
- `--worktree WORKTREE_NAME`: Name of the worktree
- `--description DESC`: Optional description of the service

**Example:**
```bash
# Allocate a web server port for worktree 'review-GH-42'
python scripts/port_allocate.py --service web --worktree review-GH-42 --description "Frontend dev server"
```

**Output:**
```
Allocating port for service 'web' in worktree 'review-GH-42'
Found available port: 8080
Registry updated: design/worktrees/ports.json
Allocated port: 8080

You can start your service with:
  npm start -- --port 8080
  python manage.py runserver 0.0.0.0:8080
```

**When to Use:**
- Before starting a new service in a worktree
- When you need to reserve a port in advance
- When documenting service requirements

### Command: Release Port

**Script:** `scripts/port_allocate.py`

**Purpose:** Release a previously allocated port.

**Usage:**
```bash
python scripts/port_allocate.py --release PORT_NUMBER
```

**Parameters:**
- `--release PORT_NUMBER`: Port number to release

**Example:**
```bash
# Release port 8080
python scripts/port_allocate.py --release 8080
```

**Output:**
```
Releasing port 8080
Port 8080 released successfully
Registry updated: design/worktrees/ports.json
```

**When to Use:**
- After removing a worktree
- When a service is no longer needed
- When reconfiguring port allocations

### Command: Check Port Status (All Ports)

**Script:** `scripts/port_status.py`

**Purpose:** Display status of all allocated ports.

**Usage:**
```bash
python scripts/port_status.py --all
```

**Example:**
```bash
python scripts/port_status.py --all
```

**Output:**
```
Port Allocation Status
======================

Service: web (8080-8099)
  8080 → review-GH-42 (web) - Frontend dev server
    Status: healthy | PID: 12345 | Allocated: 2025-12-31 10:00:00
  8081 → feature-search (web) - Search UI development
    Status: not_running | PID: - | Allocated: 2025-12-31 09:30:00
  Available: 8082-8099 (18 ports)

Service: database (5432-5439)
  5432 → review-GH-42 (database) - PostgreSQL for PR #42
    Status: healthy | PID: 67890 | Allocated: 2025-12-31 10:01:00
  Available: 5433-5439 (7 ports)

Service: testing (9000-9099)
  Available: 9000-9099 (100 ports)

Total Allocated: 3 ports
Total Available: 143 ports
```

**When to Use:**
- To get an overview of all port allocations
- Before allocating a new port
- During troubleshooting
- For documentation purposes

### Command: Check Port Status (Specific Worktree)

**Script:** `scripts/port_status.py`

**Purpose:** Display status of ports allocated to a specific worktree.

**Usage:**
```bash
python scripts/port_status.py --worktree WORKTREE_NAME
```

**Example:**
```bash
python scripts/port_status.py --worktree review-GH-42
```

**Output:**
```
Ports for Worktree: review-GH-42
===================================

Port  | Service   | Description              | Status      | PID
------|-----------|--------------------------|-------------|-------
8080  | web       | Frontend dev server      | healthy     | 12345
5432  | database  | PostgreSQL for PR #42    | healthy     | 67890
9000  | testing   | Jest test server         | not_running | -

Total: 3 ports allocated
```

**When to Use:**
- Before starting services in a worktree
- When switching to a worktree
- During worktree debugging

### Command: Find Next Available Port

**Script:** `scripts/port_allocate.py`

**Purpose:** Find the next available port in a service range without allocating it.

**Usage:**
```bash
python scripts/port_allocate.py --find-next SERVICE_TYPE
```

**Example:**
```bash
python scripts/port_allocate.py --find-next web
```

**Output:**
```
Next available port in 'web' range: 8082
Range: 8080-8099
Currently allocated: 8080, 8081
```

**When to Use:**
- To preview available ports before allocation
- When planning port usage
- For manual port configuration

---

**Continue to:** [Part 3: Conflict Detection and Health Checking](port-management-part3-conflicts-health.md)

**Last Updated:** 2025-12-31
