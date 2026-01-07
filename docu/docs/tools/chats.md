---
sidebar_position: 4
---

# Chats Interface

Mobile-first interface for browsing Gemini CLI conversations with resume functionality.

## Launch Command

```bash
npx gemini-cli-templates --chats
```

## Features

- **Resume conversations** - One-click resume button with modal dialog showing `gemini --resume {session_id}` command
- **Copy functionality** - Click to copy resume command to clipboard with visual feedback
- **Mobile-optimized** - Touch-friendly design with responsive layout
- **Real-time monitoring** - Live conversation state detection and updates
- **Conversation browsing** - View and navigate through all your Gemini CLI conversations

## 🌐 Remote Access

Combine with Cloudflare Tunnel for access from anywhere:

```bash
npx gemini-cli-templates --chats --tunnel
```

---

**Next:** Learn about [Cloudflare Tunnel](./tunnel) for secure remote access to your tools.
