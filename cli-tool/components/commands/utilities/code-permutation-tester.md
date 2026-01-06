---
name: code-permutation-tester
description: Test code snippets against various inputs and edge cases to ensure robustness.
allowed-tools: Read, Write, Bash
argument-hint: "[snippet-file] | --fuzz | --edge-cases"
---

# Code Permutation Tester

Test code snippets against a wide range of inputs, permutations, and edge cases to ensure robustness and correctness.

## Capabilities

- **Input Permutation**: Generate diverse input combinations (types, values, lengths)
- **Edge Case Fuzzing**: Test boundary conditions (empty, null, max/min values)
- **Error Handling**: Verify graceful handling of invalid inputs and exceptions
- **Output Verification**: Check output correctness against expected results

## Usage

```bash
gemini code-permutation-tester src/algorithms/sort.ts
```

## Report

Generates a report detailing:
- Total permutations tested
- Passed/Failed scenarios
- specific inputs that caused failures
- Recommendations for hardening the code
