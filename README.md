[![npm version](https://img.shields.io/npm/v/gemini-cli-templates.svg)](https://www.npmjs.com/package/gemini-cli-templates)
[![npm downloads](https://img.shields.io/npm/dt/gemini-cli-templates.svg)](https://www.npmjs.com/package/gemini-cli-templates)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Sponsored by Z.AI](https://img.shields.io/badge/Sponsored%20by-Z.AI-2563eb?style=flat&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEyIDJMMiAyMkgyMkwxMiAyWiIgZmlsbD0id2hpdGUiLz4KPC9zdmc+)](https://z.ai/subscribe?ic=8JVLJQFSKB&utm_source=github&utm_medium=badge&utm_campaign=readme)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-support-yellow?style=flat&logo=buy-me-a-coffee)](https://buymeacoffee.com/daniavila)
[![GitHub stars](https://img.shields.io/github/stars/davila7/gemini-cli-templates.svg?style=social&label=Star)](https://github.com/davila7/gemini-cli-templates)

<p align="center">
  <a href="https://trendshift.io/repositories/15113" target="_blank">
    <img src="https://trendshift.io/api/badge/repositories/15113" alt="davila7%2Fgemini-cli-templates | Trendshift" style="width: 200px; height: 40px;" width="125" height="40"/>
  </a>
  <br />
  <br />
  <a href="https://vercel.com/oss">
  <img alt="Vercel OSS Program" src="https://vercel.com/oss/program-badge.svg" />
  </a>
</p>

---

<div align="center">
  <h3>🤝 Partnership</h3>
  <p>
    <strong>This project is sponsored by <a href="https://z.ai" target="_blank">Z.AI</a></strong><br/>
    Supporting Gemini CLI Templates with the <strong>GLM CODING PLAN</strong>
  </p>
  <p>
    <a href="https://z.ai/subscribe?ic=8JVLJQFSKB&utm_source=github&utm_medium=readme&utm_campaign=partnership" target="_blank">
      <img src="https://img.shields.io/badge/Get%2010%25%20OFF-GLM%20Coding%20Plan-2563eb?style=for-the-badge" alt="GLM Coding Plan" />
    </a>
  </p>
  <p>
    <em>Top-tier coding performance powered by GLM-4.6 • Starting at $3/month</em><br/>
    <em>Seamlessly integrates with Gemini CLI, Cursor, Cline & 10+ AI coding tools</em>
  </p>
  <p>
    <code>npx gemini-cli-templates@latest --setting partnerships/glm-coding-plan --yes</code>
  </p>
</div>

---

# Gemini CLI Templates ([aitmpl.com](https://aitmpl.com))

**Ready-to-use configurations for Google's Gemini CLI.** A comprehensive collection of AI agents, custom commands, settings, hooks, external integrations (MCPs), and project templates to enhance your development workflow.

## Browse & Install Components and Templates

**[Browse All Templates](https://aitmpl.com)** - Interactive web interface to explore and install 100+ agents, commands, settings, hooks, and MCPs.

<img width="1049" height="855" alt="Screenshot 2025-08-19 at 08 09 24" src="https://github.com/user-attachments/assets/e3617410-9b1c-4731-87b7-a3858800b737" />

## 🚀 Quick Installation

```bash
# Install a complete development stack
npx gemini-cli-templates@latest --agent development-team/frontend-developer --command testing/generate-tests --mcp development/github-integration --yes

# Browse and install interactively
npx gemini-cli-templates@latest

# Install specific components
npx gemini-cli-templates@latest --agent development-tools/code-reviewer --yes
npx gemini-cli-templates@latest --command performance/optimize-bundle --yes
npx gemini-cli-templates@latest --setting performance/mcp-timeouts --yes
npx gemini-cli-templates@latest --hook git/pre-commit-validation --yes
npx gemini-cli-templates@latest --mcp database/postgresql-integration --yes
```

## What You Get

| Component       | Description                                       | Examples                                                          |
| --------------- | ------------------------------------------------- | ----------------------------------------------------------------- |
| **🤖 Agents**   | AI specialists for specific domains               | Security auditor, React performance optimizer, database architect |
| **⚡ Commands** | Custom slash commands                             | `/generate-tests`, `/optimize-bundle`, `/check-security`          |
| **🔌 MCPs**     | External service integrations                     | GitHub, PostgreSQL, Stripe, AWS, OpenAI                           |
| **⚙️ Settings** | Gemini CLI configurations                         | Timeouts, memory settings, output styles                          |
| **🪝 Hooks**    | Automation triggers                               | Pre-commit validation, post-completion actions                    |
| **🎨 Skills**   | Reusable capabilities with progressive disclosure | PDF processing, Excel automation, custom workflows                |

## 🛠️ Additional Tools

Beyond the template catalog, Gemini CLI Templates includes powerful development tools:

### 📊 Gemini CLI Analytics

Monitor your AI-powered development sessions in real-time with live state detection and performance metrics.

```bash
npx gemini-cli-templates@latest --analytics
```

### 💬 Conversation Monitor

Mobile-optimized interface to view Gemini responses in real-time with secure remote access.

```bash
# Local access
npx gemini-cli-templates@latest --chats

# Secure remote access via Cloudflare Tunnel
npx gemini-cli-templates@latest --chats --tunnel
```

### 🔍 Health Check

Comprehensive diagnostics to ensure your Gemini CLI installation is optimized.

```bash
npx gemini-cli-templates@latest --health-check
```

### 🔌 Plugin Dashboard

View marketplaces, installed plugins, and manage permissions from a unified interface.

```bash
npx gemini-cli-templates@latest --plugins
```

## 📖 Documentation

**[📚 docs.aitmpl.com](https://docs.aitmpl.com/)** - Complete guides, examples, and API reference for all components and tools.

## Contributing

We welcome contributions! **[Browse existing templates](https://aitmpl.com)** to see what's available, then check our [contributing guidelines](CONTRIBUTING.md) to add your own agents, commands, MCPs, settings, or hooks.

**Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing.**

## Attribution

This collection includes components from multiple sources:

**Scientific Skills:**

- **[K-Dense-AI/gemini-scientific-skills](https://github.com/K-Dense-AI/gemini-scientific-skills)** by K-Dense Inc. - MIT License (139 scientific skills for biology, chemistry, medicine, and computational research)

**Official Google:**

- **[googles/skills](https://github.com/googles/skills)** - Official Google skills (21 skills)
- **[googles/gemini-cli](https://github.com/googles/gemini-code)** - Development guides and examples (10 skills)

**Community Skills & Agents:**

- **[obra/superpowers](https://github.com/obra/superpowers)** by Jesse Obra - MIT License (14 workflow skills)
- **[alirezarezvani/gemini-skills](https://github.com/alirezarezvani/gemini-skills)** by Alireza Rezvani - MIT License (36 professional role skills)
- **[wshobson/agents](https://github.com/wshobson/agents)** by wshobson - MIT License (48 agents)
- **NerdyChefsAI Skills** - Community contribution - MIT License (specialized enterprise skills)

**Commands & Tools:**

- **[awesome-gemini-cli](https://github.com/hesreallyhim/awesome-gemini-code)** by hesreallyhim - CC0 1.0 Universal (21 commands)
- **[awesome-gemini-skills](https://github.com/mehdi-lamrani/awesome-gemini-skills)** - Apache 2.0 (community skills)
- **move-code-quality-skill** - MIT License
- **cocoindex-gemini** - Apache 2.0

Each of these resources retains its **original license and attribution**, as defined by their respective authors.
We respect and credit all original creators for their work and contributions to the Gemini ecosystem.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **🌐 Browse Templates**: [aitmpl.com](https://aitmpl.com)
- **📚 Documentation**: [docs.aitmpl.com](https://docs.aitmpl.com)
- **💬 Community**: [GitHub Discussions](https://github.com/davila7/gemini-code-templates/discussions)
- **🐛 Issues**: [GitHub Issues](https://github.com/davila7/gemini-code-templates/issues)

## Stargazers over time

[![Stargazers over time](https://starchart.cc/davila7/gemini-code-templates.svg?variant=adaptive)](https://starchart.cc/davila7/gemini-code-templates)

---

**⭐ Found this useful? Give us a star to support the project!**

[![Buy Me A Coffee](https://img.buymeacoffee.com/button-api/?text=Buy%20me%20a%20coffee&slug=daniavila&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff)](https://buymeacoffee.com/daniavila)
