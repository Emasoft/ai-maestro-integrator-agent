# Docker Worktree Testing - Index

This documentation covers Docker container testing with Git worktrees, split into two parts for efficient reading.

## Document Parts

### [Part 1: Setup & Configuration](docker-worktree-testing-part1-setup.md)
**~400 lines** - Use when setting up Docker worktree environments

**Table of Contents:**
1. When you need to understand Docker with worktrees - Overview
   - If you're wondering why combine Docker and worktrees - Why Combine?
   - When you need to know when to use this - Use Cases
2. When you need one container set per worktree - Container-Per-Worktree Pattern
   - If you need pattern overview - Pattern Components
   - When you want to understand the mechanism - How It Works
   - If you need naming guidelines - Container Naming Convention
3. When you need Docker Compose configuration - Docker Compose Per Worktree
   - If you need template structure - Template Structure
   - When you need template details - Template Explanation
4. When you need dynamic ports - Dynamic Port Configuration
   - If you need port assignment process - Port Assignment Flow
   - When generating environment files - Environment File Generation
   - If avoiding port conflicts - Port Conflict Avoidance
5. When you need a complete example - Workflow Example

---

### [Part 2: Best Practices & Troubleshooting](docker-worktree-testing-part2-best-practices.md)
**~430 lines** - Use for optimization and problem-solving

**Table of Contents:**
1. If you need implementation guidelines - Best Practices
   - When naming containers - Container Naming Conventions
   - If setting resource limits - Resource Limits Per Worktree
   - When cleaning up containers - Cleanup Procedures
   - If managing data persistence - Data Persistence Strategy
   - When isolating networks - Network Isolation
   - If managing environment files - Environment File Management
   - When implementing health checks - Health Checks
2. If you need advanced techniques - Advanced Patterns
   - When you need Docker expertise - Linking to Docker Container Expert Skill
3. When you encounter Docker problems - Troubleshooting
   - If port is already in use
   - If container name conflicts
   - If database connection refused
   - If volume permission issues
   - If old data in containers
   - If slow build times
   - If can't access service from host
4. If you need a quick summary - Summary

---

## Quick Reference

| Need | Read |
|------|------|
| Initial setup and patterns | [Part 1](docker-worktree-testing-part1-setup.md) |
| Docker Compose templates | [Part 1](docker-worktree-testing-part1-setup.md) |
| Port allocation | [Part 1](docker-worktree-testing-part1-setup.md) |
| Step-by-step workflow | [Part 1](docker-worktree-testing-part1-setup.md) |
| Resource limits | [Part 2](docker-worktree-testing-part2-best-practices.md) |
| Cleanup procedures | [Part 2](docker-worktree-testing-part2-best-practices.md) |
| Health checks | [Part 2](docker-worktree-testing-part2-best-practices.md) |
| Troubleshooting errors | [Part 2](docker-worktree-testing-part2-best-practices.md) |

## Related Documentation

- `worktree-creation.md` - Creating worktrees
- `port-allocation.md` - Port management system
- `worktree-removal.md` - Cleanup procedures
- `docker-container-expert` skill - Advanced Docker patterns
