# Registry System

## Table of Contents

This document is split into parts for efficient progressive disclosure. Read only the sections relevant to your current task.

---

## Part 1: Schema and Location

**File:** [registry-system-part1-schema.md](./registry-system-part1-schema.md)

**Contents:**
- 1.1 When you need to understand the registry system → Overview
- 1.2 If you need to find the registry file → Registry Location
- 1.3 When you need to understand registry structure → Registry Schema
  - 1.3.1 If you need to see a complete example → Full Schema Example
  - 1.3.2 When you need to understand entry fields → Worktree Entry Fields
  - 1.3.3 If you need to know valid purpose types → Purpose Categories
  - 1.3.4 When you need to understand status meanings → Status Values
  - 1.3.5 If you need to configure port ranges → Port Ranges Section
  - 1.3.6 When you need to understand naming templates → Naming Convention Section

---

## Part 2: Operations

**File:** [registry-system-part2-operations.md](./registry-system-part2-operations.md)

**Contents:**
- 2.1 When you need to modify the registry → Registry Operations
  - 2.1.1 If you're adding a new worktree → Create Entry
  - 2.1.2 When you need to change worktree state → Update Status
  - 2.1.3 If you're deleting a worktree → Remove Entry
  - 2.1.4 When you need to find worktrees by type → Query by Purpose
  - 2.1.5 If you need to find worktree by issue → Query by Issue

---

## Part 3: Validation Rules

**File:** [registry-system-part3-validation.md](./registry-system-part3-validation.md)

**Contents:**
- 3.1 When you need to enforce registry rules → Validation Rules
  - 3.1.1 If you need to check ID uniqueness → Unique IDs
  - 3.1.2 When you need to validate paths → Valid Paths
  - 3.1.3 If you're checking port conflicts → No Port Conflicts
  - 3.1.4 When you need to validate status → Valid Status Values
  - 3.1.5 If you're verifying required fields → Required Fields Present

---

## Part 4: Automatic Cleanup and Troubleshooting

**File:** [registry-system-part4-cleanup.md](./registry-system-part4-cleanup.md)

**Contents:**
- 4.1 When you need to clean stale entries → Automatic Cleanup
  - 4.1.1 If you need to identify stale entries → What is a Stale Entry?
  - 4.1.2 When you need the detection logic → Stale Detection Algorithm
  - 4.1.3 If you need to run cleanup → Cleanup Process
  - 4.1.4 When you need to force cleanup → Manual Cleanup Override
- 4.2 If you encounter registry problems → Troubleshooting
  - 4.2.1 Registry File Corrupted
  - 4.2.2 Port Already in Use (but not in registry)
  - 4.2.3 Duplicate IDs After Manual Edit
  - 4.2.4 Worktree Exists but Not in Registry
- 4.3 When you need additional context → Related References

---

## Quick Reference

| Task | Read This Part |
|------|----------------|
| Understand what the registry does | Part 1: Overview |
| Find registry file location | Part 1: Registry Location |
| Understand JSON structure | Part 1: Registry Schema |
| Add/update/remove entries | Part 2: Operations |
| Validate registry data | Part 3: Validation Rules |
| Clean up stale worktrees | Part 4: Automatic Cleanup |
| Fix registry problems | Part 4: Troubleshooting |
