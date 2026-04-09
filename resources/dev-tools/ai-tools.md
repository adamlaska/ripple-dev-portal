---
seo:
    description: Accelerate development on the XRPL with AI tools.
---
# AI Tools

AI tools help you build on the XRP Ledger faster by giving AI models access to up-to-date XRPL documentation, SDK references, and code samples.


## Model Context Protocol (MCP) Servers

AI models are limited by their training data, which may not include the latest XRPL features or SDK updates. MCP servers solve this by giving your AI real-time access to current documentation through a standardized interface. Instead of relying on potentially outdated training data, your AI can query an MCP server for accurate, up-to-date context. Below is a list of available MCP servers:

- **Context7**: A large collection of searchable repos and websites. XRPL-relevant info includes:
    - [xrpl.org](https://xrpl.org/docs)
    - [opensource.ripple.com](https://opensource.ripple.com/)
    - [docs.xrplevm.org](https://docs.xrplevm.org/)
    - [XRPL JavaScript SDK](https://github.com/xrplf/xrpl.js)
    - [XRPL Python SDK](https://github.com/xrplf/xrpl-py)
    - [XRPL Go SDK](https://github.com/xrplf/xrpl-go)
- **xrpl.org MCP Server**: Search across documentation on xrpl.org for a given query.


## SKILLS.md

A SKILLS.md file provides behavioral instructions for AI models working with XRPL code. It defines domain-specific rules — like transaction validation, fee handling, and security best practices — so the AI follows correct patterns without you having to explain them each time.

- **[XRPL Development Skill for Claude Code](https://github.com/XRPL-Commons/xrpl-dev-skills)**: A comprehensive Claude Code skill for modern XRP Ledger development, provided by XRPL Commons. This skill uses Claude Code's progressive disclosure pattern. The main `SKILL.md` provides core guidance, and Claude reads specialized markdown files only when needed for specific tasks.
- **[Generate Release Notes](https://github.com/XRPLF/xrpl-dev-portal/blob/master/.claude/skills/generate-release-notes/SKILL.md)**: This skill generates a draft release notes blog post for new versions of `rippled`. This is intended for those contributing to the XRPL documentation site.


## Site Optimizations

### AI Search

We include an AI chatbot on xrpl.org, opensource.ripple.com, and docs.xrplevm.org to provide a more natural-language approach to searching documentation. You can access this feature either through the **Ask AI** button on the bottom right of the website, or the **Search with AI** button from the search bar.

### llms.txt

The site hosts an `llms.txt` file at the root directory, providing a curated index of content for AI crawlers and tools to find relevant information quickly.

### Context Optimization

Markdown files are the best format to feed an LLM context. Every page on the doc site hosts an `.md` version, which is accessible from the `Copy` dropdown at the top of the page. The copy options include:

- Copy the contents of the raw `.md` file.
- Copy a link to the `.md` version of the page.
- Open the page in a `Claude` or `ChatGPT` chat window.
- Set up the xrpl.org MCP server in `VS Code` or `Cursor` with one click.
