# GEMINI.md

This file provides guidance to Gemini Code (gemini.ai/code) when working with code in this repository.

## Project Overview

This is a GenAI-native application built with **Gemini 3** capabilities, specifically focusing on the **Nano Banana Pro** (Gemini 3 Pro Image) model.

## Gemini 3 Capabilities

This project leverages the following advanced capabilities:

### Nano Banana Pro (Gemini 3 Pro Image Preview)
- **Model Name**: `gemini-3-pro-image-preview`
- **Capabilities**:
    - **Visual Design**: Create professional assets, posters, intricate diagrams.
    - **Advanced Reasoning ("Thinking")**: Can follow complex instructions and understand nuance.
    - **High-Fidelity Text Rendering**: Generates clear, legible text within images.
    - **World Knowledge**: Incorporates real-world context into generated visuals.

### Nano Banana (Gemini 2.5 Flash Image)
- **Model Name**: `gemini-2.5-flash-image`
- **Capabilities**: High-volume, low-latency image generation.

## Development Guidelines

### Image Generation
- Use `gemini-3-pro-image-preview` for tasks requiring high detail, text rendering, or complex composition.
- Use `gemini-2.5-flash-image` for rapid prototyping or high-throughput tasks.
- When generating images with text, explicitly specify the text content and style in the prompt.

### Prompting Strategy
- **Nano Banana Pro** supports complex prompts. Be descriptive and specific about:
    - Subject matter
    - Style and medium (e.g., "oil painting", "vector art", "photorealistic")
    - Composition and lighting
    - Text elements (e.g., "with the text 'Hello World' in neon letters")

### Code Integration
- Use the official Google Gen AI SDKs.
- Handle image data appropriately (e.g., save to file, return as buffer).
- Implement error handling for API quotas and content safety filters.

## Project Structure

```
.
├── .gemini/             # Gemini configuration
├── .mcp.json            # Model Context Protocol configuration
├── main.py / index.js   # Application entry point
└── output/              # Directory for generated assets
```

## Security & Safety
- Do not hardcode API keys. Use `GEMINI_API_KEY` environment variable.
- Review generated content for safety and alignment with project goals.
