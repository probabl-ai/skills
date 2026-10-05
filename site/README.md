# Probabl Skills site

Static page for the skills catalog, built with Astro and Tailwind. It is published at <https://probabl-ai.github.io/skills/>.

The page reads skill titles, summaries, categories, and workflow packs from `../.catalog.json` at build time.

## Commands

The `site` Pixi environment provides Node.js. From the repository root:

| Command | Action |
| --- | --- |
| `pixi run -e site site-install` | Install dependencies from `package-lock.json` |
| `pixi run -e site site-dev` | Start the dev server |
| `pixi run -e site site-build` | Write the production site to `dist/` |

`site-dev` and `site-build` run `site-install` first.

## Fonts

Headings use IBM Plex Serif, licensed under the SIL Open Font License (`src/fonts/OFL.txt`). Body and mono text use the system fallbacks from the Probabl marketing type stack. Suisse Intl is a commercial face and is not vendored in this public repository.

## GitHub Pages

`.github/workflows/pages.yml` sets up the `site` Pixi environment, runs `site-build`, and publishes `dist/`. It runs on pushes to `main` that change `site/`, `.catalog.json`, or the Pixi manifest and lock, and when someone runs the workflow by hand.

A repo admin turns Pages on once: Settings → Pages → Source **GitHub Actions**. If that setting is turned on after the workflow is already on `main`, run **Pages** with **Run workflow**.
