---
seo:
    description: Accelerate development on the XRPL with AI tools.
---
# AI Tools

The industry has shifted sharply toward _Agentic Workflows_ to accelerate development, automate integrations, and deploy secure solutions on the XRP Ledger. To meet this growing segment of developers, we provide AI tools to reduce hallucinations, automate tasks, and improve code generation.


## Model Context Protocol (MCP) Servers

Ensure your LLM uses the latest infoThe direct data pipe for AI. The Model Context Protocol (MCP) allows your AI tools to skip the "search and scrape" phase. By connecting your IDE to the XRPL MCP server, you provide your LLM with a real-time, version-accurate stream of markdown files from the official repository.
Connect to the Context7 agentic registry to import the full XRPL knowledge base.
CTA: [Context7 MCP]


## Agent Intelligence & Skills (SKILLS.md)
Logic-level guardrails for autonomous agents. Raw data is not enough for secure financial deployments. We are introducing official SKILLS.md files—standardized behavioral instructions that act as a "firmware update" for your AI models.
Deterministic Logic: Forces LLMs to follow strict transaction fee handling and sequence logic.
Compliance & Security: Teaches models to prioritize multisig configurations and check for active network amendments (like XLS-30 or XLS-66) before proposing code.
Status: [Coming Soon] 


## Site Optimizations

### llms.txt

Any AI that searches the website has access to an `llms.txt` file at the site directory root. This file serves as a curated index of content, ensuring it can find relevant information quickly.

### Context-Optimization

Markdown files are the best format to feed an LLM context. Every page on the doc site hosts an `.md` version, which is accessible from the `Copy` dropdown at the top of the page. The full list of copy commands include:

- Copying the contents of the raw `.md` file.
- A link to the `.md` version of the page.
- A button that adds the page URL to a chat window in either `Claude` or `ChatGPT` chat windows.
- A one-click MCP server setup in either `VS Code` or `Cursor`.


 Every page has a markdown version

## RAG-Optimized Infrastructure
The site architecture is being optimized for Retrieval-Augmented Generation (RAG).
Semantic Precision
The core pages are undergoing a semantic audit to eliminate ambiguous language and implement self-contained chunking. 
When your RAG pipeline retrieves a snippet, it contains all the context necessary for the LLM to understand the logic without needing to crawl adjacent pages.
The llms.txt Standard
The site hosts a specialized llms.txt index. This serves as a high-density "map" for crawlers, ensuring your AI assistants are always referencing the official source of truth.
Overall Developer Experience 
We have removed the friction between the documentation and the codebase with features designed for high-stakes environments.
Copy for LLM: Powered by Redocly, our code samples feature a specialized "Copy for LLM" button. This removes UI clutter and formats the code with the metadata headers LLMs need for perfect prompt injection.
Hybrid Tutorials: Our guides are built as "Modular Lego Blocks." They provide the narrative "Why" for human reviewers and the deterministic "How" for AI agents to execute without confusion.
