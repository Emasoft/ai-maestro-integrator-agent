# JavaScript/TypeScript Review Patterns Reference

This is the index file for JavaScript/TypeScript code review patterns. Content is split into multiple parts for efficient loading.

---

## Table of Contents

### Part 1: Style, Types, and Modules
**File:** [javascript-review-patterns-part1-style-types-modules.md](javascript-review-patterns-part1-style-types-modules.md)

- **3.1 JavaScript/TypeScript Code Style Checklist**
  - 3.1.1 Essential style rules table (indentation, naming, etc.)
  - 3.1.2 Modern JavaScript features to use (const/let, arrow functions, destructuring, optional chaining)
  - 3.1.3 Formatting checklist

- **3.2 Type Safety Patterns in TypeScript**
  - 3.2.1 Essential type patterns (primitives, arrays, interfaces, generics, utility types)
  - 3.2.2 Strict mode tsconfig.json configuration
  - 3.2.3 Type safety checklist
  - 3.2.4 Common TypeScript errors and fixes table

- **3.3 Module System Considerations (ESM vs CommonJS)**
  - 3.3.1 ES Modules (ESM) import/export syntax
  - 3.3.2 CommonJS (CJS) require/exports syntax
  - 3.3.3 Choosing module system decision table
  - 3.3.4 Package.json dual-format configuration
  - 3.3.5 Module system checklist

---

### Part 2: Testing and Linting
**File:** [javascript-review-patterns-part2-testing-linting.md](javascript-review-patterns-part2-testing-linting.md)

- **3.4 Test Framework Patterns with Jest and Vitest**
  - 3.4.1 Jest project structure
  - 3.4.2 Jest configuration (jest.config.ts)
  - 3.4.3 Jest test patterns (mocking, describe/it, assertions)
  - 3.4.4 Vitest configuration (vitest.config.ts)
  - 3.4.5 Test review checklist

- **3.5 Linting with ESLint and Prettier**
  - 3.5.1 ESLint flat config configuration
  - 3.5.2 Prettier configuration (.prettierrc)
  - 3.5.3 Running linters (CLI commands)
  - 3.5.4 Package.json scripts for linting
  - 3.5.5 Linting review checklist

---

## Quick Reference: When to Read Each Part

| If you need to review... | Read this part |
|--------------------------|----------------|
| Code style, naming conventions | Part 1, Section 3.1 |
| TypeScript types, strict mode | Part 1, Section 3.2 |
| Import/export, ESM vs CJS | Part 1, Section 3.3 |
| Jest or Vitest tests | Part 2, Section 3.4 |
| ESLint or Prettier config | Part 2, Section 3.5 |

---

## Summary Checklists

### Code Style Quick Check
- [ ] 2-space indentation
- [ ] Consistent semicolons and quotes
- [ ] camelCase variables, PascalCase classes
- [ ] Modern features (const/let, arrow functions, optional chaining)

### TypeScript Quick Check
- [ ] No `any` without justification
- [ ] Strict mode enabled
- [ ] Proper null checking

### Module System Quick Check
- [ ] Package.json has `"type"` field
- [ ] Consistent import syntax

### Testing Quick Check
- [ ] Descriptive test names
- [ ] Independent tests
- [ ] Error cases covered

### Linting Quick Check
- [ ] ESLint passes
- [ ] Prettier applied
- [ ] TypeScript compiles
