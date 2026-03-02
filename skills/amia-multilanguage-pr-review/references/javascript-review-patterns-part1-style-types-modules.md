# JavaScript/TypeScript Review Patterns - Part 1: Style, Types, and Modules

This document covers code style conventions, TypeScript type safety, and module systems.

## Table of Contents

- [3.1 JavaScript/TypeScript Code Style Checklist](#31-javascripttypescript-code-style-checklist)
  - [Essential Style Rules](#essential-style-rules)
  - [Modern JavaScript Features to Use](#modern-javascript-features-to-use)
  - [Formatting Checklist](#formatting-checklist)
- [3.2 Type Safety Patterns in TypeScript](#32-type-safety-patterns-in-typescript)
  - [Essential Type Patterns](#essential-type-patterns)
  - [Strict Mode Configuration](#strict-mode-configuration)
  - [Type Safety Checklist](#type-safety-checklist)
  - [Common TypeScript Errors and Fixes](#common-typescript-errors-and-fixes)
- [3.3 Module System Considerations (ESM vs CommonJS)](#33-module-system-considerations-esm-vs-commonjs)
  - [ES Modules (ESM) - Modern Standard](#es-modules-esm---modern-standard)
  - [CommonJS (CJS) - Node.js Legacy](#commonjs-cjs---nodejs-legacy)
  - [Choosing Module System](#choosing-module-system)
  - [Package.json Configuration](#packagejson-configuration)
  - [Module System Checklist](#module-system-checklist)

---

## 3.1 JavaScript/TypeScript Code Style Checklist

Modern JavaScript/TypeScript should follow consistent conventions.

### Essential Style Rules

| Rule | Good | Bad |
|------|------|-----|
| Indentation | 2 spaces | Tabs or 4 spaces |
| Semicolons | Consistent (prefer with) | Mixed usage |
| Quotes | Single or double (consistent) | Mixed quotes |
| Naming: variables | `camelCase` | `snake_case`, `PascalCase` |
| Naming: classes | `PascalCase` | `camelCase`, `snake_case` |
| Naming: constants | `SCREAMING_SNAKE_CASE` or `camelCase` | Mixed conventions |
| Naming: interfaces | `PascalCase` (no I prefix) | `IInterface` |
| Naming: types | `PascalCase` | `camelCase` |
| Trailing commas | Yes, in multiline | No trailing commas |
| Arrow functions | Preferred for callbacks | `function` for callbacks |

### Modern JavaScript Features to Use

```typescript
// Use const/let, never var
const immutableValue = 42;
let mutableValue = 0;

// Use arrow functions for callbacks
const doubled = numbers.map((n) => n * 2);

// Use destructuring
const { name, age } = user;
const [first, second, ...rest] = items;

// Use template literals
const message = `Hello, ${name}! You are ${age} years old.`;

// Use optional chaining
const city = user?.address?.city ?? 'Unknown';

// Use nullish coalescing
const value = input ?? defaultValue;

// Use object shorthand
const user = { name, age, email };

// Use spread operator
const merged = { ...defaults, ...overrides };
const combined = [...array1, ...array2];

// Use async/await over promises
async function fetchData() {
  const response = await fetch(url);
  return response.json();
}
```

### Formatting Checklist

- [ ] Consistent semicolon usage
- [ ] Consistent quote style
- [ ] No trailing whitespace
- [ ] Blank line at end of file
- [ ] Imports at top of file
- [ ] No unused variables or imports
- [ ] Consistent brace style (same line opening)
- [ ] Spaces around operators
- [ ] No nested ternaries (use if/else or extract to function)

---

## 3.2 Type Safety Patterns in TypeScript

TypeScript provides static typing for JavaScript.

### Essential Type Patterns

```typescript
// Primitive types
const name: string = 'Alice';
const age: number = 30;
const isActive: boolean = true;

// Arrays
const numbers: number[] = [1, 2, 3];
const strings: Array<string> = ['a', 'b', 'c'];

// Objects with interfaces
interface User {
  id: number;
  name: string;
  email: string;
  role: 'admin' | 'user' | 'guest';  // Union literal types
  createdAt: Date;
  metadata?: Record<string, unknown>;  // Optional property
}

// Type aliases
type UserID = number;
type UserMap = Map<UserID, User>;
type Callback<T> = (value: T) => void;

// Generics
function identity<T>(value: T): T {
  return value;
}

interface Repository<T> {
  get(id: number): Promise<T | null>;
  save(entity: T): Promise<T>;
  delete(id: number): Promise<boolean>;
}

// Utility types
type PartialUser = Partial<User>;           // All props optional
type RequiredUser = Required<User>;          // All props required
type ReadonlyUser = Readonly<User>;          // All props readonly
type UserKeys = keyof User;                  // 'id' | 'name' | ...
type PickedUser = Pick<User, 'id' | 'name'>; // Only id and name
type OmittedUser = Omit<User, 'metadata'>;   // All except metadata
```

### Strict Mode Configuration

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "strictBindCallApply": true,
    "strictPropertyInitialization": true,
    "noImplicitThis": true,
    "useUnknownInCatchVariables": true,
    "alwaysStrict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedIndexedAccess": true,
    "forceConsistentCasingInFileNames": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  }
}
```

### Type Safety Checklist

- [ ] No `any` types without justification
- [ ] No `@ts-ignore` without explanation comment
- [ ] No non-null assertions (`!`) without justification
- [ ] Union types used instead of `any` where possible
- [ ] Generics used for reusable components
- [ ] Interface over type alias for object shapes
- [ ] Strict mode enabled
- [ ] No implicit any (parameter types declared)
- [ ] Proper error handling with typed errors

### Common TypeScript Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `'X' is possibly 'undefined'` | Nullable value access | Add null check or optional chaining |
| `Argument of type 'X' is not assignable` | Type mismatch | Fix type or add type assertion |
| `Property 'X' does not exist` | Wrong property name | Check spelling or add to interface |
| `Cannot find module 'X'` | Missing type definitions | Install @types/X or declare module |
| `Object is possibly 'null'` | Null value access | Add null check |

---

## 3.3 Module System Considerations (ESM vs CommonJS)

JavaScript has two module systems with different syntax and behavior.

### ES Modules (ESM) - Modern Standard

```typescript
// Importing
import defaultExport from 'module';
import { namedExport } from 'module';
import { namedExport as alias } from 'module';
import * as moduleNamespace from 'module';
import type { TypeOnly } from 'module';  // TypeScript type import

// Exporting
export const value = 42;
export function func() {}
export class MyClass {}
export default class DefaultClass {}
export type { TypeOnly };  // TypeScript type export

// Re-exporting
export { something } from 'other-module';
export * from 'other-module';
```

### CommonJS (CJS) - Node.js Legacy

```javascript
// Importing
const module = require('module');
const { namedExport } = require('module');

// Exporting
module.exports = defaultExport;
module.exports.namedExport = namedExport;
exports.namedExport = namedExport;
```

### Choosing Module System

| Scenario | Recommendation |
|----------|----------------|
| New Node.js project | ESM with `"type": "module"` |
| New browser project | ESM (bundler handles) |
| Library for both | ESM with CJS fallback |
| Legacy Node.js | CJS for compatibility |
| TypeScript project | ESM with transpilation |

### Package.json Configuration

```json
{
  "name": "my-package",
  "type": "module",
  "main": "./dist/index.cjs",
  "module": "./dist/index.js",
  "types": "./dist/index.d.ts",
  "exports": {
    ".": {
      "import": {
        "types": "./dist/index.d.ts",
        "default": "./dist/index.js"
      },
      "require": {
        "types": "./dist/index.d.cts",
        "default": "./dist/index.cjs"
      }
    }
  }
}
```

### Module System Checklist

- [ ] Package.json has explicit `"type"` field
- [ ] File extensions match module system (.js, .mjs, .cjs)
- [ ] TypeScript moduleResolution matches output
- [ ] Imports use correct syntax for module system
- [ ] No mixing require() and import in same file
- [ ] Dynamic imports use `await import()` syntax
