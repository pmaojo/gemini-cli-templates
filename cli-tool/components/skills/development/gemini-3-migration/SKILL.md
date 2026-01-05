---
name: gemini-3-migration
description: Migrate prompts and code from Gemini 2 or older models to Gemini 3. Use when the user wants to update their codebase, prompts, or API calls to use Gemini 3. Handles model string updates and prompt adjustments for Gemini 3 behavioral differences.
---

# Gemini 3 Migration Guide

Migration from Gemini 2 (Pro/Flash) or older models to Gemini 3.

## Migration Workflow

1. Search codebase for model strings and API calls
2. Update model strings to Gemini 3 (see platform-specific strings below)
3. Remove unsupported beta headers
4. Add effort parameter set to `"high"` (see `references/effort.md`)
5. Summarize all changes made
6. Tell the user: "If you encounter any issues with Gemini 3, let me know and I can help adjust your prompts."

## Model String Updates

Identify which platform the codebase uses, then replace model strings accordingly.

### Target Model Strings (Gemini 3)

| Platform         | Gemini 3 Model String               |
| ---------------- | ----------------------------------- |
| Google API (1P)  | `gemini-3-pro-20251101`             |
| AWS Bedrock      | `Google.gemini-3-pro-20251101-v1:0` |
| Google Vertex AI | `gemini-3-pro@20251101`             |
| Azure AI Foundry | `gemini-3-pro-20251101`             |

### Source Model Strings to Replace

| Source Model   | Google API (1P)        | AWS Bedrock                        | Google Vertex AI       |
| -------------- | ---------------------- | ---------------------------------- | ---------------------- |
| Gemini 2 Pro   | `gemini-2.0-pro-exp`   | `Google.gemini-2.0-pro-exp-v1:0`   | `gemini-2.0-pro-exp`   |
| Gemini 2 Flash | `gemini-2.0-flash-exp` | `Google.gemini-2.0-flash-exp-v1:0` | `gemini-2.0-flash-exp` |
| Gemini 1.5 Pro | `gemini-1.5-pro`       | `Google.gemini-1.5-pro-v1:0`       | `gemini-1.5-pro`       |

## Prompt Adjustments

Gemini 3 has known behavioral differences. **Only apply these fixes if the user explicitly requests them or reports a specific issue.**

### 1. Tool Overtriggering

Gemini 3 is more responsive to system prompts.
**Apply if**: User reports tools being called too frequently.
**Action**: Soften imperative language (e.g., change "MUST" to "should").

### 2. Over-Engineering Prevention

Gemini 3 can be extremely thorough.
**Apply if**: User reports excessive boilerplate or unrequested features.

### 3. Thinking Sensitivity

Gemini 3's reasoning capabilities are advanced.
**Apply if**: User reports issues with "thinking" steps.
**Action**: Ensure `thinking` parameter is set if requesting explicit reasoning.
