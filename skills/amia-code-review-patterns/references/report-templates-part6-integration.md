# Integration Report Template

Template for documenting system integration status and component interactions.

---

## Template

```markdown
# Integration Report
**Generated**: YYYY-MM-DD HH:MM:SS
**Scope**: [System/Components]

## Integration Status: 🟢 HEALTHY / 🟡 ISSUES / 🔴 BROKEN

## Component Interaction Map

╔════════════════════╦═══════════════════╦═══════════════╦═══════════╗
║ Source             ║ Target            ║ Interface     ║ Status    ║
╠════════════════════╬═══════════════════╬═══════════════╬═══════════╣
║ Frontend           ║ API Gateway       ║ REST API      ║ ✅ OK     ║
║ API Gateway        ║ Auth Service      ║ gRPC          ║ ✅ OK     ║
║ Auth Service       ║ Database          ║ PostgreSQL    ║ ⚠️ Slow   ║
║ API Gateway        ║ Cache             ║ Redis         ║ ✅ OK     ║
╚════════════════════╩═══════════════════╩═══════════════╩═══════════╝

## API Contract Verification

- **OpenAPI Spec Version**: 3.0.1
- **Breaking Changes**: None detected
- **Deprecated Endpoints**: 2 (scheduled removal: v2.0)

## Integration Test Results

- **Total**: 45 tests
- **Passed**: 43
- **Failed**: 2
- **Coverage**: 89%

## Issues Detected

1. **Auth Service -> Database**: Response time increased 40%
   - **Impact**: Login latency
   - **Resolution**: Query optimization needed

---
**Report ID**: integration_YYYYMMDD_HHMMSS
```

---

## Integration Status Types

| Status | Meaning |
|--------|---------|
| 🟢 HEALTHY | All integrations working normally |
| 🟡 ISSUES | Some integrations degraded |
| 🔴 BROKEN | Critical integration failures |

## Component Status Icons

| Icon | Meaning |
|------|---------|
| ✅ OK | Integration working normally |
| ⚠️ Slow | Performance degradation |
| ❌ Fail | Integration broken |

## Common Interface Types

| Type | Description |
|------|-------------|
| REST API | HTTP-based RESTful interface |
| gRPC | High-performance RPC protocol |
| PostgreSQL | Direct database connection |
| Redis | Cache/message broker connection |
| WebSocket | Real-time bidirectional communication |

---

**Back to [Report Templates Index](report-templates.md)**
