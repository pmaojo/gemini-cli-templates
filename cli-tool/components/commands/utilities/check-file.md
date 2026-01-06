---
name: check-file
description: Detailed file analysis for potential issues, code quality, and security vulnerabilities.
allowed-tools: Read, Bash
argument-hint: [file-path]
---

# Check File

Perform detailed analysis of a specific file for potential issues, code quality, and security vulnerabilities.

## Analysis Steps

1. **Syntax Check**: Verify syntax correctness for the file type
2. **Linting**: Run applicable linters to identify style and quality issues
3. **Security Scan**: Check for common security vulnerabilities (secrets, injection, etc.)
4. **Complexity Analysis**: Assess code complexity and maintainability metrics
5. **Best Practices**: Verify adherence to language-specific best practices

## Usage

```bash
gemini check-file src/utils/helper.ts
```

## Output

- **Summary**: Overview of findings (Errors, Warnings, Info)
- **Detailed Issues**: List of identified issues with line numbers and descriptions
- **Recommendations**: actionable suggestions for improvement
