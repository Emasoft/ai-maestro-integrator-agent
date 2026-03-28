# Integration Phase Procedures

## Contents

- [Phase 1: Request Reception](#phase-1-request-reception)
  - [1. Check AI Maestro Inbox](#1-check-ai-maestro-inbox)
  - [2. Extract Request Details](#2-extract-request-details)
  - [3. Log Request](#3-log-request)
- [Phase 2: Routing Decision](#phase-2-routing-decision)
  - [1. Analyze Request Type](#1-analyze-request-type)
  - [2. Check Sub-Agent Availability](#2-check-sub-agent-availability)
  - [3. Prepare Context Package](#3-prepare-context-package)
  - [4. Create Status Tracking File](#4-create-status-tracking-file)
- [Phase 3: Delegation](#phase-3-delegation)
  - [1. Draft Delegation Message](#1-draft-delegation-message)
  - [2. Send to Sub-Agent](#2-send-to-sub-agent)
  - [3. Log Delegation](#3-log-delegation)
- [Phase 4: Monitor Completion](#phase-4-monitor-completion)
  - [1. Wait for Sub-Agent Response](#1-wait-for-sub-agent-response)
  - [2. Validate Response Format](#2-validate-response-format)
  - [3. Read Result Details](#3-read-result-details)
  - [4. Update Status File](#4-update-status-file)
- [Phase 5: Report to AMOA](#phase-5-report-to-amoa)
  - [1. Prepare Status Report](#1-prepare-status-report)
  - [2. Send to AMOA](#2-send-to-amoa)
  - [3. Handle Blockers (If Any)](#3-handle-blockers-if-any)
  - [4. Final Logging](#4-final-logging)
- [Verification Summary](#verification-summary)

This document provides step-by-step procedures for each integration phase. Follow these procedures in order to ensure consistent and reliable integration operations.

---

## Phase 1: Request Reception

### 1. Check AI Maestro Inbox

- Read unread messages from AMOA or other requestors
- Parse message content for request type and context
- **Verification**: Request format is valid and complete

### 2. Extract Request Details

- Identify: PR number, issue number, branch name, error logs
- Determine: request type, priority, success criteria
- **Verification**: All required context present

### 3. Log Request

- Append to `docs_dev/integration/routing-log.md`
- Format: `[timestamp] RECEIVE request_type from requestor`
- **Verification**: Log entry written

---

## Phase 2: Routing Decision

### 1. Analyze Request Type

- Match against routing table (see "Sub-Agent Routing")
- Apply "When to Use Judgment" rules
- **Verification**: Routing decision is justified

### 2. Check Sub-Agent Availability

- Verify target sub-agent is not busy
- Confirm sub-agent has necessary skills loaded
- **Verification**: Sub-agent can accept task

### 3. Prepare Context Package

- Use Glob to find affected files
- Read error logs if present
- Extract PR/issue descriptions
- **Verification**: Context is complete

### 4. Create Status Tracking File

- Write to `docs_dev/integration/status/[task-id].md`
- Include: request details, routing decision, status: DELEGATED
- **Verification**: Status file created

---

## Phase 3: Delegation

### 1. Draft Delegation Message

- Use appropriate AI Maestro template (see "AI Maestro Message Templates")
- Include: task, context, success criteria, callback agent
- **Verification**: Message is actionable

### 2. Send to Sub-Agent

- Send message using the `agent-messaging` skill
- Wait for acknowledgment (30 second timeout)
- **Verification**: Sub-agent acknowledged

### 3. Log Delegation

- Append to routing log: `[timestamp] ROUTE request_type -> sub-agent`
- Include rationale for routing decision
- **Verification**: Delegation logged

---

## Phase 4: Monitor Completion

### 1. Wait for Sub-Agent Response

- Poll AI Maestro inbox (or receive notification)
- Check for messages from delegated sub-agent
- **Verification**: Response received within expected time

### 2. Validate Response Format

- Confirm: `[DONE/FAILED] sub-agent - brief_result`
- Extract: result status, details file path
- **Verification**: Response format is correct

### 3. Read Result Details

- Access log/report file specified by sub-agent
- Verify: quality gates status, test results, findings
- **Verification**: Results are complete

### 4. Update Status File

- Change status to COMPLETED or FAILED
- Include: completion timestamp, result summary, quality gates status
- **Verification**: Status file updated

---

## Phase 5: Report to AMOA

### 1. Prepare Status Report

- Use "Reporting Integration Status" template
- Include: result, quality gates, merge status, next steps
- **Verification**: Report is comprehensive

### 2. Send to AMOA

- Send message to orchestrator-amoa using the `agent-messaging` skill
- Include link to detailed report file
- **Verification**: Message sent

### 3. Handle Blockers (If Any)

- If FAILED or BLOCKED, use "Escalating Blockers" template
- Include: blocker type, details, recommendation
- Mark as requiring decision
- **Verification**: Escalation sent with urgency

### 4. Final Logging

- Append to routing log: `[timestamp] COMPLETE task-id`
- Include: result, details file path
- **Verification**: Completion logged

---

## Verification Summary

Each phase includes verification checkpoints to ensure:

- **Completeness**: All required information is present
- **Correctness**: Data format and content are valid
- **Traceability**: Actions are logged for audit
- **Accountability**: Status updates are written
- **Communication**: Messages are sent and acknowledged
