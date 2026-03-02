# Port Management

This document has been split into 5 parts for easier navigation and consumption.

## Parts Overview

| Part | File | Topics | Lines |
|------|------|--------|-------|
| 1 | [port-management-part1-overview-registry.md](port-management-part1-overview-registry.md) | Overview, Port Registry Structure | ~240 |
| 2 | [port-management-part2-allocation-cli.md](port-management-part2-allocation-cli.md) | Allocation Functions, CLI Commands | ~430 |
| 3 | [port-management-part3-conflicts-health.md](port-management-part3-conflicts-health.md) | Conflict Detection, Health Checking | ~410 |
| 4 | [port-management-part4-docker.md](port-management-part4-docker.md) | Docker Compose Integration | ~230 |
| 5 | [port-management-part5-troubleshooting.md](port-management-part5-troubleshooting.md) | Troubleshooting, Summary | ~365 |

## Quick Navigation by Topic

### Getting Started
- [What is a Port?](port-management-part1-overview-registry.md#what-is-a-port)
- [Why Port Management is Needed](port-management-part1-overview-registry.md#why-port-management-is-needed)
- [Port Range Organization](port-management-part1-overview-registry.md#port-range-organization)

### Registry Configuration
- [Registry File Location](port-management-part1-overview-registry.md#registry-file-location)
- [Full Registry Schema](port-management-part1-overview-registry.md#full-registry-schema)
- [Initializing a New Registry](port-management-part1-overview-registry.md#initializing-a-new-registry)

### Port Allocation
- [allocate_port() Function](port-management-part2-allocation-cli.md#function-allocate_port)
- [release_port() Function](port-management-part2-allocation-cli.md#function-release_port)
- [check_port_available() Function](port-management-part2-allocation-cli.md#function-check_port_available)
- [list_allocated_ports() Function](port-management-part2-allocation-cli.md#function-list_allocated_ports)

### CLI Commands
- [Allocate Port Command](port-management-part2-allocation-cli.md#command-allocate-port)
- [Release Port Command](port-management-part2-allocation-cli.md#command-release-port)
- [Check Port Status](port-management-part2-allocation-cli.md#command-check-port-status-all-ports)
- [Find Next Available Port](port-management-part2-allocation-cli.md#command-find-next-available-port)

### Conflict Management
- [Types of Conflicts](port-management-part3-conflicts-health.md#types-of-conflicts)
- [Automated Conflict Detection](port-management-part3-conflicts-health.md#automated-conflict-detection)

### Health Monitoring
- [Health Check Levels](port-management-part3-conflicts-health.md#health-check-levels)
- [Health Status Values](port-management-part3-conflicts-health.md#health-status-values)
- [Running Health Checks](port-management-part3-conflicts-health.md#running-health-checks)
- [Automated Health Monitoring](port-management-part3-conflicts-health.md#automated-health-monitoring)

### Docker Integration
- [Dynamic Port Mapping Strategy](port-management-part4-docker.md#dynamic-port-mapping-strategy)
- [Single Service Example](port-management-part4-docker.md#example-single-service)
- [Multiple Services Example](port-management-part4-docker.md#example-multiple-services)
- [Automation Scripts](port-management-part4-docker.md#automation-script)

### Troubleshooting
- [Port Already in Use](port-management-part5-troubleshooting.md#problem-port-already-in-use)
- [Registry Shows Port as Free but It's in Use](port-management-part5-troubleshooting.md#problem-registry-shows-port-as-free-but-its-in-use)
- [Service Can't Bind to Allocated Port](port-management-part5-troubleshooting.md#problem-service-cant-bind-to-allocated-port)
- [Docker Container Can't Connect to Port](port-management-part5-troubleshooting.md#problem-docker-container-cant-connect-to-port)
- [Health Check Reports "not_running" but Service is Running](port-management-part5-troubleshooting.md#problem-health-check-reports-not_running-but-service-is-running)
- [Port Range is Exhausted](port-management-part5-troubleshooting.md#problem-port-range-is-exhausted)

---

**Related Documents:**
- [Worktree Fundamentals](worktree-fundamentals-index.md)
- [Registry System](registry-system.md)
- [Creating Worktrees](creating-worktrees.md)
- [Troubleshooting](troubleshooting-index.md)

**Last Updated:** 2026-01-10
