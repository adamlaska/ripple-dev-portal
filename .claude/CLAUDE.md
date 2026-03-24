# XRPL Dev Portal — Claude Code Instructions

## Quick Reference

- **Framework:** Redocly Realm v0.130.4
- **Stack:** React 19, TypeScript, SCSS (Bootstrap 4.6.2)
- **Branch:** `master`
- **Dev server:** `npm start`
- **Build CSS:** `npm run build-css`

## Content Authoring

- Documentation lives in `docs/` with YAML frontmatter (`seo.title`, `seo.description`, `labels`, `html`, `parent`)
- Blog posts go in `blog/<year>/` with `date`, `category` (year), and `template` fields
- Use Markdoc tags: `{% admonition %}`, `{% tabs %}`, `{% child-pages /%}`, `{% repo-link %}`
- Reusable snippets live in `docs/_snippets/`, code samples in `_code-samples/`, API examples in `_api-examples/`
- Environment variables are interpolated with `{% $env.PUBLIC_VAR_NAME %}`

## Code Conventions

- Functional React components with TypeScript interfaces for props
- Use `clsx` for conditional class names
- All user-facing strings go through `translate()` from `useThemeHooks()`
- Bootstrap 4.6.2 class names (not Tailwind)
- SCSS partials in `styles/scss/`, compiled to `static/css/devportal2024-v1.css`

## Localization

- Default: `en-US`, supported: `ja` (Japanese)
- Translations mirror `docs/` structure under `@l10n/ja/`

## Navigation

- Update `sidebars.yaml` when adding new doc pages
- Top nav is configured in `top-nav.yaml`
- Redirects go in `redirects.yaml`
