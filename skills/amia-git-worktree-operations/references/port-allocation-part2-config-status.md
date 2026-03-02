# Port Allocation: Configuration & Status

## Table of Contents

1. [If you need to generate worktree configurations → Configuration Templates](#configuration-templates)
2. [When you need to check port status → Port Status Commands](#port-status-commands)

---

## Configuration Templates

### What is a Configuration Template?

A **configuration template** is a file with placeholder variables that get replaced with actual allocated port numbers.

### Template File Example

**File: `.env.worktree.template`**
```bash
# Web Server Configuration
WEB_PORT=${ALLOCATED_WEB_PORT}
WEB_HOST=localhost

# Database Configuration
DB_PORT=${ALLOCATED_DB_PORT}
DB_HOST=localhost
DB_NAME=myapp_${WORKTREE_NAME}

# Test Server Configuration
TEST_PORT=${ALLOCATED_TEST_PORT}
TEST_HOST=localhost

# Debug Server Configuration
DEBUG_PORT=${ALLOCATED_DEBUG_PORT}
DEBUG_HOST=localhost

# API Configuration
API_PORT=${ALLOCATED_API_PORT}
API_BASE_URL=http://localhost:${ALLOCATED_API_PORT}
```

### Generating Configuration from Template

```python
def generate_worktree_config(worktree_name, template_path, output_path):
    """
    Generate a worktree-specific configuration file from template.

    Args:
        worktree_name: Name of the worktree
        template_path: Path to template file
        output_path: Where to write the generated config
    """
    # Get allocated ports for this worktree
    registry = load_registry()
    ports = registry["allocated_ports"][worktree_name]

    # Read template
    with open(template_path, 'r') as f:
        template = f.read()

    # Replace placeholders
    config = template.replace('${ALLOCATED_WEB_PORT}', str(ports['web']))
    config = config.replace('${ALLOCATED_DB_PORT}', str(ports['db']))
    config = config.replace('${ALLOCATED_TEST_PORT}', str(ports['test']))
    config = config.replace('${ALLOCATED_DEBUG_PORT}', str(ports['debug']))
    config = config.replace('${WORKTREE_NAME}', worktree_name)

    # Write output
    with open(output_path, 'w') as f:
        f.write(config)

    print(f"Generated config: {output_path}")
```

### Generated Configuration Example

**File: `feature-payment/.env.worktree`**
```bash
# Web Server Configuration
WEB_PORT=8082
WEB_HOST=localhost

# Database Configuration
DB_PORT=5434
DB_HOST=localhost
DB_NAME=myapp_feature-payment

# Test Server Configuration
TEST_PORT=9002
TEST_HOST=localhost

# Debug Server Configuration
DEBUG_PORT=5557
DEBUG_HOST=localhost

# API Configuration
API_PORT=3002
API_BASE_URL=http://localhost:3002
```

### Using Configuration in Code

**JavaScript/Node.js:**
```javascript
// Load environment variables
require('dotenv').config({ path: '.env.worktree' });

// Use allocated ports
const webPort = process.env.WEB_PORT;
const dbPort = process.env.DB_PORT;

app.listen(webPort, () => {
  console.log(`Server running on port ${webPort}`);
});
```

**Python:**
```python
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.worktree')

# Use allocated ports
web_port = int(os.getenv('WEB_PORT'))
db_port = int(os.getenv('DB_PORT'))

app.run(host='localhost', port=web_port)
```

---

## Port Status Commands

### List All Allocated Ports

**Command:**
```bash
eia port list
```

**Output:**
```
Worktree Port Allocations
═════════════════════════════════════════════════════════

Worktree: main
├── Web Server:    8080 (http://localhost:8080)
├── Database:      5432 (postgresql://localhost:5432)
├── Test Server:   9000 (http://localhost:9000)
└── Debug Server:  5555 (ws://localhost:5555)

Worktree: feature-login
├── Web Server:    8081 (http://localhost:8081)
├── Database:      5433 (postgresql://localhost:5433)
├── Test Server:   9001 (http://localhost:9001)
└── Debug Server:  5556 (ws://localhost:5556)

Worktree: feature-payment
├── Web Server:    8082 (http://localhost:8082)
├── Database:      5434 (postgresql://localhost:5434)
├── Test Server:   9002 (http://localhost:9002)
└── Debug Server:  5557 (ws://localhost:5557)

Port Usage Summary:
Web:   3/20 ports used (15%)
DB:    3/8 ports used (37%)
Test:  3/100 ports used (3%)
Debug: 3/10 ports used (30%)
```

### Check Port Availability

**Command:**
```bash
eia port check <port_number>
```

**Example:**
```bash
$ eia port check 8083

Port 8083 Status
═════════════════════════════════════════════════════════
Status:      AVAILABLE
Range:       web (8080-8099)
Next in use: 8082 (feature-payment)
```

**Example (port in use):**
```bash
$ eia port check 8081

Port 8081 Status
═════════════════════════════════════════════════════════
Status:      IN USE
Allocated:   feature-login
Service:     web
Started:     2024-01-15 14:30:22
```

### Check Ports for Specific Worktree

**Command:**
```bash
eia port show <worktree_name>
```

**Example:**
```bash
$ eia port show feature-login

Ports for Worktree: feature-login
═════════════════════════════════════════════════════════
Web Server:    8081  [LISTENING]
Database:      5433  [LISTENING]
Test Server:   9001  [NOT LISTENING]
Debug Server:  5556  [NOT LISTENING]

To start all services:
  cd feature-login && npm start
```

### Release Ports Manually

**Command:**
```bash
eia port release <worktree_name>
```

**Example:**
```bash
$ eia port release feature-login

Releasing ports for: feature-login
═════════════════════════════════════════════════════════
✓ Released port 8081 (web)
✓ Released port 5433 (db)
✓ Released port 9001 (test)
✓ Released port 5556 (debug)

Ports are now available for reallocation.
```

---

## Related Documents

- [Core Concepts](port-allocation-part1-core-concepts.md) - Why ports matter and allocation algorithm
- [Conflict Resolution & Docker](port-allocation-part3-conflict-docker.md) - Handling conflicts and Docker integration
- [Cleanup & Troubleshooting](port-allocation-part4-cleanup-troubleshooting.md) - Port cleanup and problem solving
