# JavaScript/TypeScript Review Patterns - Part 2: Testing and Linting

This document covers test framework patterns and linting configuration.

## Table of Contents

- [3.4 Test Framework Patterns with Jest and Vitest](#34-test-framework-patterns-with-jest-and-vitest)
  - [Jest Project Structure](#jest-project-structure)
  - [Jest Configuration](#jest-configuration)
  - [Jest Test Patterns](#jest-test-patterns)
  - [Vitest Configuration](#vitest-configuration)
  - [Test Review Checklist](#test-review-checklist)
- [3.5 Linting with ESLint and Prettier](#35-linting-with-eslint-and-prettier)
  - [ESLint Configuration (Flat Config)](#eslint-configuration-flat-config)
  - [Prettier Configuration](#prettier-configuration)
  - [Running Linters](#running-linters)
  - [Package.json Scripts](#packagejson-scripts)
  - [Linting Review Checklist](#linting-review-checklist)

---

## 3.4 Test Framework Patterns with Jest and Vitest

### Jest Project Structure

```
project/
├── src/
│   ├── utils.ts
│   └── services/
│       └── userService.ts
├── tests/
│   ├── setup.ts
│   ├── utils.test.ts
│   └── services/
│       └── userService.test.ts
├── jest.config.ts
└── package.json
```

### Jest Configuration

```typescript
// jest.config.ts
import type { Config } from 'jest';

const config: Config = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/tests'],
  setupFilesAfterEnv: ['<rootDir>/tests/setup.ts'],
  collectCoverageFrom: ['src/**/*.ts', '!src/**/*.d.ts'],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
};

export default config;
```

### Jest Test Patterns

```typescript
// tests/services/userService.test.ts
import { UserService } from '@/services/userService';
import { Database } from '@/database';

// Mock the database module
jest.mock('@/database');

describe('UserService', () => {
  let userService: UserService;
  let mockDb: jest.Mocked<Database>;

  beforeEach(() => {
    mockDb = new Database() as jest.Mocked<Database>;
    userService = new UserService(mockDb);
    jest.clearAllMocks();
  });

  describe('createUser', () => {
    it('should create a user with valid data', async () => {
      const userData = { name: 'Alice', email: 'alice@example.com' };
      mockDb.insert.mockResolvedValue({ id: 1, ...userData });

      const user = await userService.createUser(userData);

      expect(user.id).toBe(1);
      expect(user.name).toBe('Alice');
      expect(mockDb.insert).toHaveBeenCalledWith('users', userData);
    });

    it('should throw on invalid email', async () => {
      const userData = { name: 'Bob', email: 'invalid' };

      await expect(userService.createUser(userData))
        .rejects.toThrow('Invalid email format');

      expect(mockDb.insert).not.toHaveBeenCalled();
    });
  });

  describe('findByEmail', () => {
    it.each([
      ['alice@example.com', { id: 1, name: 'Alice' }],
      ['bob@example.com', { id: 2, name: 'Bob' }],
    ])('should find user with email %s', async (email, expected) => {
      mockDb.query.mockResolvedValue(expected);

      const user = await userService.findByEmail(email);

      expect(user).toEqual(expected);
    });
  });
});
```

### Vitest Configuration

Vitest is a faster Jest alternative for Vite projects.

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';
import { resolve } from 'path';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    include: ['tests/**/*.test.ts'],
    setupFiles: ['tests/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      include: ['src/**/*.ts'],
      exclude: ['src/**/*.d.ts'],
    },
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
});
```

### Test Review Checklist

- [ ] Tests have descriptive names
- [ ] Each test verifies one behavior
- [ ] Tests are independent (no order dependency)
- [ ] Mocks are properly typed
- [ ] Async tests use async/await properly
- [ ] Error cases are tested
- [ ] Edge cases are covered
- [ ] No hardcoded timeouts (use fake timers)
- [ ] Setup/teardown properly cleans up

---

## 3.5 Linting with ESLint and Prettier

### ESLint Configuration (Flat Config)

```typescript
// eslint.config.js
import eslint from '@eslint/js';
import tseslint from 'typescript-eslint';
import prettier from 'eslint-config-prettier';

export default tseslint.config(
  eslint.configs.recommended,
  ...tseslint.configs.strictTypeChecked,
  ...tseslint.configs.stylisticTypeChecked,
  {
    languageOptions: {
      parserOptions: {
        project: true,
        tsconfigRootDir: import.meta.dirname,
      },
    },
    rules: {
      '@typescript-eslint/explicit-function-return-type': 'error',
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
      '@typescript-eslint/no-explicit-any': 'error',
      '@typescript-eslint/prefer-nullish-coalescing': 'error',
      '@typescript-eslint/prefer-optional-chain': 'error',
      'no-console': 'warn',
      'eqeqeq': ['error', 'always'],
    },
  },
  {
    files: ['**/*.test.ts', '**/*.spec.ts'],
    rules: {
      '@typescript-eslint/no-explicit-any': 'off',
    },
  },
  prettier,  // Must be last to disable formatting rules
);
```

### Prettier Configuration

```json
// .prettierrc
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "all",
  "printWidth": 100,
  "bracketSpacing": true,
  "arrowParens": "always",
  "endOfLine": "lf"
}
```

### Running Linters

```bash
# ESLint
npx eslint .                      # Check for issues
npx eslint --fix .                # Auto-fix issues
npx eslint --cache .              # Use cache for speed

# Prettier
npx prettier --check .            # Check formatting
npx prettier --write .            # Fix formatting

# TypeScript
npx tsc --noEmit                  # Type check without emitting

# Combined (recommended in package.json)
npm run lint                      # Run all linters
```

### Package.json Scripts

```json
{
  "scripts": {
    "lint": "eslint . && prettier --check .",
    "lint:fix": "eslint --fix . && prettier --write .",
    "typecheck": "tsc --noEmit",
    "test": "vitest run",
    "test:watch": "vitest",
    "test:coverage": "vitest run --coverage"
  }
}
```

### Linting Review Checklist

- [ ] ESLint passes with no errors
- [ ] Prettier formatting is applied
- [ ] TypeScript type checking passes
- [ ] No eslint-disable without explanation
- [ ] No @ts-ignore without explanation
- [ ] Warnings are addressed or explicitly allowed
- [ ] Rules are consistent across project
