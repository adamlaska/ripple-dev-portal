# AGENTS.md

## Project Overview

This is the **XRP Ledger Dev Portal** ([xrpl.org](https://xrpl.org)), the authoritative documentation site for the XRP Ledger. It is built with [Redocly Realm](https://redocly.com/) and uses React 19, TypeScript, and SCSS.

The primary branch is `master`.

## Build and Dev Commands

```bash
npm install          # Install dependencies
npm start            # Local dev server (realm develop)
npm run build-css    # Compile SCSS → static/css/devportal2024-v1.css
npm run build-css-watch  # Watch mode for SCSS
```

There is no dedicated test suite or linter configured at the project level.

## Directory Structure

| Path | Purpose |
|------|---------|
| `docs/` | Core documentation (concepts, tutorials, references, infrastructure, use-cases) |
| `docs/_snippets/` | Reusable markdown partials |
| `blog/` | Blog posts organized by year (2014–2026) |
| `_code-samples/` | Multi-language example code (JS, TS, Python, Go, Java, PHP) |
| `_api-examples/` | API request/response JSON examples |
| `@theme/` | Custom Redocly theme (React components, plugins, Markdoc schema) |
| `@l10n/ja/` | Japanese translations |
| `@l10n/es-ES/` | Spanish translations (incomplete) |
| `shared/components/` | Shared React components used across pages |
| `styles/scss/` | SCSS partials (Bootstrap 4.6.2 base) |
| `static/` | Static assets (compiled CSS, JS, images, fonts) |
| `resources/` | Developer resources and tools |
| `community/` | Community pages |

## Content Conventions

### Markdown Frontmatter

Documentation pages use YAML frontmatter:

```yaml
---
html: page-name.html
parent: parent-section.html
seo:
  title: "Page Title"
  description: "SEO description"
labels:
  - Category
---
```

Blog posts include `date`, `category` (year), and a `template` field pointing to `@theme/templates/blogpost`.

### Markdoc Custom Tags

The project extends Markdown with Markdoc tags:

- `{% admonition type="success/warning/info" %}` — callout boxes
- `{% child-pages /%}` — auto-generated child page lists
- `{% tabs %}{% tab label="..." %}` — tabbed content
- `{% $env.PUBLIC_BASE_RESERVE %}` — environment variable interpolation
- `{% repo-link %}` — links to source repo
- `{% code-page-name %}` — code sample references

### Markdown Partials

Partials are sourced from three directories (configured in `redocly.yaml`):
- `docs/_snippets/`
- `_code-samples/`
- `_api-examples/`

## Code Style

### TypeScript / React

- Functional components with TypeScript interfaces for props
- `clsx` for conditional CSS class names
- Internationalization via `useThemeHooks()` → `useTranslate()` → `translate()`
- Page-level TSX files export a `frontmatter` object for SEO metadata
- Bootstrap 4.6.2 class names throughout (`container-new`, `col-lg-8`, `py-26`, etc.)

### SCSS

- 40+ partials in `styles/scss/`, organized by component/feature
- Compiled with `sass --style=compressed` to `static/css/devportal2024-v1.css`
- Bootstrap 4.6.2 as the base framework

## Localization

- Default locale: `en-US`
- Supported: `ja` (Japanese) — translations mirror `docs/` structure under `@l10n/ja/`
- Spanish (`es-ES`) exists but is incomplete
- All user-facing strings in React components use the `translate()` function

## Configuration Files

| File | Purpose |
|------|---------|
| `redocly.yaml` | Main site config (locales, search, SEO, analytics, markdown partials) |
| `sidebars.yaml` | Documentation sidebar navigation |
| `top-nav.yaml` | Top navigation bar structure |
| `redirects.yaml` | URL redirect mappings |
| `translations.yaml` | Localization configuration |
| `tsconfig.json` | TypeScript compiler options |
| `.env` | Public environment variables (reserve amounts, GitHub URLs) |

## Pull Request Guidelines

- Keep documentation changes focused — one topic per PR when possible
- Ensure any new pages have proper frontmatter with `seo` fields
- Code samples should include implementations in as many supported languages as practical
- Update `sidebars.yaml` when adding new documentation pages
- Verify Markdoc syntax renders correctly with `npm start` before submitting

## Security Considerations

- The `.env` file contains only public values (reserve amounts, GitHub URLs) — no secrets
- Static assets are served from `static/` — do not place sensitive files there
- Code samples should never include real private keys or credentials
