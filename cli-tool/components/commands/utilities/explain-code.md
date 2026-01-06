---
name: explain-code
description: Explain complex code segments in plain language with examples.
allowed-tools: Read
argument-hint: [file-path] | --line=[n-m] | --detail=high|low
---

# Explain Code

Explain complex code segments, algorithms, or entire files in plain language.

## Capabilities

- **Code Breakdown**: Step-by-step explanation of code logic
- **Algorithm Analysis**: Explain complexity and behavior of algorithms
- **Contextualization**: Explain code within the context of the project
- **Examples**: Generate usage examples for functions and classes

## Usage

```bash
gemini explain-code src/complex-algo.ts
gemini explain-code src/utils.ts --line=50-100
```

## Security Best Practices

When analyzing authentication flows:

1. Identify authentication mechanisms in request headers
2. Validate token signatures and expiration
3. Ensure secure storage of sensitive data
4. Verify proper error handling for auth failures
