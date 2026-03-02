# Port Allocation: Core Concepts

## Table of Contents

1. [When you need to understand why ports matter → Why Port Allocation is Needed](#why-port-allocation-is-needed)
2. [If you need to understand port organization → Understanding Port Ranges](#understanding-port-ranges)
3. [When you need to know how ports are assigned → Port Allocation Algorithm](#port-allocation-algorithm)

**Related Documents:**
- [Part 2: Configuration & Status](./port-allocation-part2-config-status.md) - Configuration templates, port status commands
- [Part 3: Conflict Resolution & Docker](./port-allocation-part3-conflict-docker.md) - Conflict handling, Docker integration
- [Part 4: Cleanup & Troubleshooting](./port-allocation-part4-cleanup-troubleshooting.md) - Port cleanup, troubleshooting, quick reference

---

## Why Port Allocation is Needed

### The Problem

When you run multiple worktrees of the same project simultaneously, each worktree may need to start its own services (web servers, databases, test runners, debug servers). If all worktrees try to use the same port numbers, you get **port conflicts**.

**Example of a port conflict:**
```bash
# Worktree 1 starts web server on port 8080
cd ~/projects/myapp/main
npm start  # Uses port 8080 ✓

# Worktree 2 tries to start web server on port 8080
cd ~/projects/myapp/feature-login
npm start  # ERROR: Port 8080 already in use ✗
```

### The Solution

**Port allocation** is a system that automatically assigns unique port numbers to each worktree, preventing conflicts.

**How it works:**
1. Each worktree gets its own set of unique ports
2. Ports are tracked in a central registry
3. Configuration files use allocated ports instead of hardcoded values
4. Ports are released when worktrees are deleted

---

## Understanding Port Ranges

### What is a Port?

A **port** is a number (0-65535) that identifies a specific service on a computer. When a program listens on a port, other programs can connect to it using that port number.

### Standard Port Ranges

Different types of services use different port number ranges to stay organized:

| Service Type | Port Range | Example Usage |
|--------------|------------|---------------|
| **Web Servers** | 8080-8099 | Development web servers (HTTP) |
| **Databases** | 5432-5439 | PostgreSQL, MySQL instances |
| **Testing Services** | 9000-9099 | Test runners, mock servers |
| **Debug Servers** | 5555-5564 | Node.js debugger, Python debugger |
| **API Servers** | 3000-3099 | REST APIs, GraphQL endpoints |
| **WebSocket Servers** | 9100-9199 | Real-time communication |

### Why These Ranges?

1. **Avoid System Ports** (0-1023): Reserved for operating system services
2. **Avoid Common Ports** (e.g., 3000, 5432): Often used by default configurations
3. **Grouped by Purpose**: Easy to remember and manage
4. **Sufficient Space**: 20-100 ports per range allows many worktrees

### Example Port Set for One Worktree

```
Worktree: feature-login
├── Web Server:    8081
├── Database:      5433
├── Test Server:   9001
├── Debug Server:  5556
└── API Server:    3001
```

---

## Port Allocation Algorithm

### Step-by-Step Process

#### Step 1: Check the Registry

The **port registry** is a file that tracks which ports are currently allocated to which worktrees.

**Registry location:**
```
.git/worktree-registry/ports.json
```

**Registry format:**
```json
{
  "allocated_ports": {
    "main": {
      "web": 8080,
      "db": 5432,
      "test": 9000,
      "debug": 5555
    },
    "feature-login": {
      "web": 8081,
      "db": 5433,
      "test": 9001,
      "debug": 5556
    }
  },
  "port_ranges": {
    "web": [8080, 8099],
    "db": [5432, 5439],
    "test": [9000, 9099],
    "debug": [5555, 5564]
  }
}
```

#### Step 2: Find Next Available Port

For each service type, scan the range to find the first unused port:

```python
def find_available_port(service_type, registry):
    """
    Find the next available port in the range for a service type.

    Args:
        service_type: "web", "db", "test", or "debug"
        registry: Loaded port registry data

    Returns:
        int: Available port number
    """
    # Get the range for this service type
    start, end = registry["port_ranges"][service_type]

    # Get all currently allocated ports for this service type
    used_ports = set()
    for worktree_ports in registry["allocated_ports"].values():
        if service_type in worktree_ports:
            used_ports.add(worktree_ports[service_type])

    # Find first available port in range
    for port in range(start, end + 1):
        if port not in used_ports:
            return port

    # No ports available in range
    raise Exception(f"No available ports in {service_type} range")
```

**Example:**
```python
# Web ports: 8080-8099
# Already used: 8080 (main), 8081 (feature-login)
# Next available: 8082

port = find_available_port("web", registry)
# Returns: 8082
```

#### Step 3: Reserve Port in Registry

Once an available port is found, add it to the registry:

```python
def allocate_ports(worktree_name, registry):
    """
    Allocate a complete set of ports for a new worktree.

    Args:
        worktree_name: Name of the worktree
        registry: Loaded port registry data

    Returns:
        dict: Allocated ports for all service types
    """
    allocated = {}

    # Allocate a port for each service type
    for service_type in ["web", "db", "test", "debug"]:
        port = find_available_port(service_type, registry)
        allocated[service_type] = port

    # Add to registry
    registry["allocated_ports"][worktree_name] = allocated

    # Save registry back to disk
    save_registry(registry)

    return allocated
```

**Example output:**
```python
allocate_ports("feature-payment", registry)
# Returns:
# {
#     "web": 8082,
#     "db": 5434,
#     "test": 9002,
#     "debug": 5557
# }
```

#### Step 4: Return Allocated Ports

The allocation function returns the port numbers that can be written to configuration files.

---

## Next Steps

Continue to [Part 2: Configuration & Status](./port-allocation-part2-config-status.md) for:
- Configuration templates
- Port status commands
