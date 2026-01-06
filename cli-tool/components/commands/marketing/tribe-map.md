---
name: tribe-map
description: Command to map the competitive landscape based on provided URLs.
---

# Tribe Map Command

Map the competitive landscape.

## Parameters

- `urls`: Space-separated list of competitor URLs.

## Usage

`gemini tribe:map "url1 url2"`

## Workflow

1. Use Puppeteer or WebFetch to analyze the provided competitor websites.
2. Identify their positioning, target audience, and core message.
3. Provide data to the `marketing:xy` agent to find the Lonely Quadrant.
