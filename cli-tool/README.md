[![npm version](https://img.shields.io/npm/v/gemini-cli-templates.svg)](https://www.npmjs.com/package/gemini-cli-templates)
[![npm downloads](https://img.shields.io/npm/dt/gemini-cli-templates.svg)](https://www.npmjs.com/package/gemini-cli-templates)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Open Source](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)](https://opensource.org/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/pmaojo/gemini-cli-templates/blob/main/CONTRIBUTING.md)
[![GitHub stars](https://img.shields.io/github/stars/pmaojo/gemini-cli-templates.svg?style=social&label=Star)](https://github.com/pmaojo/gemini-cli-templates)

# Gemini CLI Templates

**CLI tool for configuring and monitoring Gemini CLI** - Quick setup for any project with framework-specific commands and real-time monitoring dashboard. Powered by Gemini 3 and Gemini 2.0.

## 🚀 Quick Start

```bash
# Interactive setup (recommended)
npx github:pmaojo/gemini-cli-templates

# Real-time analytics dashboard
npx github:pmaojo/gemini-cli-templates --analytics

# System health check
npx github:pmaojo/gemini-cli-templates --health-check
```

## ✨ Core Features

- **📋 Smart Project Setup** - Auto-detect and configure any project with framework-specific commands
- **📊 Real-time Analytics** - Monitor Gemini CLI sessions with live state detection and performance metrics
- **🔍 Health Check** - Comprehensive system validation with actionable recommendations
- **🧩 Individual Components** - Install specialized agents, commands, and MCPs individually
- **🌍 Global Agents** - Create AI agents accessible from anywhere using Gemini CLI SDK

## 🎯 What You Get

| Component     | Description                                      | Example                                                      |
| ------------- | ------------------------------------------------ | ------------------------------------------------------------ |
| **GEMINI.md** | Project-specific Gemini CLI configuration        | Framework best practices, coding standards                   |
| **Commands**  | Custom slash commands for development tasks      | `/generate-tests`, `/check-file`, `/optimize-bundle`         |
| **Agents**    | AI specialists for specific domains              | API security audit, React performance, database optimization |
| **MCPs**      | External service integrations                    | GitHub, databases, development tools                         |
| **Skills**    | Modular capabilities with progressive disclosure | PDF processing, algorithmic art, MCP builder                 |
| **Analytics** | Real-time monitoring dashboard                   | Live session tracking, usage statistics, exports             |

## 🛠️ Supported Technologies

| Language                  | Frameworks                   | Status         | Supported Models     |
| ------------------------- | ---------------------------- | -------------- | -------------------- |
| **JavaScript/TypeScript** | React, Vue, Angular, Node.js | ✅ Ready       | Gemini 3, Gemini 2.0 |
| **Python**                | Django, Flask, FastAPI       | ✅ Ready       | Gemini 3, Gemini 2.0 |
| **Common**                | Universal configurations     | ✅ Ready       | Gemini 3, Gemini 2.0 |
| **Go**                    | Gin, Echo, Fiber             | 🚧 Coming Soon | Gemini 3, Gemini 2.0 |
| **Rust**                  | Axum, Warp, Actix            | 🚧 Coming Soon | Gemini 3, Gemini 2.0 |

## 🌍 Global Agents (Gemini CLI SDK Integration)

Create AI agents that can be executed from anywhere using the Gemini CLI SDK:

```bash
# Create a global agent (one-time setup)
npx github:pmaojo/gemini-cli-templates --create-agent customer-support

# Use the agent from anywhere
customer-support "Help me with ticket #12345"
sre-logs "Analyze error patterns in app.log"
code-reviewer "Review this PR for security issues"
```

### Available Global Agents

| Agent                            | Usage                                                  | Description                    |
| -------------------------------- | ------------------------------------------------------ | ------------------------------ |
| `customer-support`               | `customer-support "query"`                             | AI customer support specialist |
| `api-security-audit`             | `api-security-audit "analyze endpoints"`               | Security auditing for APIs     |
| `react-performance-optimization` | `react-performance-optimization "optimize components"` | React performance expert       |
| `database-optimization`          | `database-optimization "improve queries"`              | Database performance tuning    |

### Global Agent Management

```bash
# List installed global agents
npx github:pmaojo/gemini-cli-templates --list-agents

# Update an agent to latest version
npx github:pmaojo/gemini-cli-templates --update-agent customer-support

# Remove an agent
npx github:pmaojo/gemini-cli-templates --remove-agent customer-support
```

### How It Works

1. **Download Agent**: Fetches the latest agent from GitHub
2. **Generate Executable**: Creates a Node.js script that calls Gemini CLI SDK
3. **Add to PATH**: Makes the agent available globally in your shell
4. **Ready to Use**: Execute `agent-name "your prompt"` from any directory

The agents use the Gemini CLI SDK internally to provide specialized AI assistance with domain-specific knowledge and best practices.

## 🎨 Skills (Google Format)

Install modular capabilities that Gemini loads dynamically using Google's progressive disclosure pattern:

```bash
# Install individual skills
npx github:pmaojo/gemini-cli-templates --skill pdf-processing-pro
npx github:pmaojo/gemini-cli-templates --skill algorithmic-art
npx github:pmaojo/gemini-cli-templates --skill mcp-builder

# Install multiple skills
npx github:pmaojo/gemini-cli-templates --skill pdf-google,docx,xlsx,pptx
```

### Featured Skills

#### 🎨 Creative & Design

- **algorithmic-art** - Create generative art using p5.js with seeded randomness
- **canvas-design** - Design beautiful visual art in .png and .pdf formats
- **slack-gif-creator** - Create animated GIFs optimized for Slack

#### 💻 Development & Technical

- **mcp-builder** - Guide for creating high-quality MCP servers
- **artifacts-builder** - Build complex HTML artifacts with React and Tailwind
- **webapp-testing** - Test local web applications using Playwright
- **skill-creator** - Guide for creating effective skills

#### 📄 Document Processing

- **pdf-processing-pro** - Production-ready PDF toolkit (forms, tables, OCR)
- **pdf-google** - Google's comprehensive PDF manipulation toolkit
- **docx** - Create, edit, and analyze Word documents
- **xlsx** - Create, edit, and analyze Excel spreadsheets
- **pptx** - Create, edit, and analyze PowerPoint presentations

#### 🏢 Enterprise & Communication

- **brand-guidelines** - Apply Google's official brand guidelines
- **internal-comms** - Write internal communications (reports, newsletters, FAQs)
- **theme-factory** - Style artifacts with professional themes

### Skills Architecture

Skills follow Google's progressive disclosure pattern:

- **Metadata** - Always loaded (name, description)
- **Instructions** - Loaded when skill is triggered
- **Resources** - Reference files loaded only when needed
- **Scripts** - Execute without loading code into context

### Attribution

Skills from [googles/skills](https://github.com/googles/skills):

- **Open Source** (Apache 2.0): algorithmic-art, mcp-builder, skill-creator, artifacts-builder, and more
- **Source-Available** (Reference): docx, pdf-google, pptx, xlsx

## 📖 Documentation

**[📚 Complete Documentation](https://docs.gemini-cli-templates.vercel.app-templates.vercel.app/)** - Comprehensive guides, examples, and API reference

Quick links:

- [Getting Started](https://docs.gemini-cli-templates.vercel.app-templates.vercel.app/docs/intro) - Installation and first steps
- [Project Setup](https://docs.gemini-cli-templates.vercel.app-templates.vercel.app/docs/project-setup/interactive-setup) - Configure your projects
- [Analytics Dashboard](https://docs.gemini-cli-templates.vercel.app-templates.vercel.app/docs/analytics/overview) - Real-time monitoring
- [Individual Components](https://docs.gemini-cli-templates.vercel.app-templates.vercel.app/docs/components/overview) - Agents, Commands, MCPs
- [CLI Options](https://docs.gemini-cli-templates.vercel.app-templates.vercel.app/docs/cli-options) - All available commands

## 🤝 Contributing

We welcome contributions! Browse available templates and components at **[gemini-cli-templates.vercel.app](https://gemini-cli-templates.vercel.app)**, then check our [contributing guidelines](https://github.com/pmaojo/gemini-cli-templates/blob/main/CONTRIBUTING.md).

## 📄 License

MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **🌐 Browse Components**: [gemini-cli-templates.vercel.app](https://gemini-cli-templates.vercel.app)
- **📚 Documentation**: [docs.gemini-cli-templates.vercel.app](https://docs.gemini-cli-templates.vercel.app)
- **🐛 Issues**: [GitHub Issues](https://github.com/pmaojo/gemini-cli-templates/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/pmaojo/gemini-cli-templates/discussions)

---

**⭐ Found this useful? Give us a star to support the project!**
