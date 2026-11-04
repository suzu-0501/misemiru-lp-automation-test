# Misemiru LP Automation — sandbox

A public, fictional **LP foundation test** for ミセミルWeb. No client data is stored here.

## Scope
- This repository is an **automation test**, not an actual customer site.
- Initial sample goal: publish a QA-checked page on **GitHub Pages** and share the link with the customer after human review.
- Production hosting and domains are **out of scope until a signed contract and required payment confirmations**.
- Keep code changes on feature branches. Request a separate human reviewer before merging to `main`.

## Local development
Requires Node.js 20 or newer.

```bash
npm install
npm run dev
npm run lint
npm run build
```

Visit http://localhost:3000 while running the dev server.

## GitHub Pages
The site uses Next.js static export (`output: 'export'`). In GitHub Actions only, `GITHUB_PAGES=true` enables a repository-specific `basePath`.
1. Prepare and preview the LP on a feature branch. Pull requests to `main` run lint, build and visual-preview checks without publication.
2. Obtain explicit human approval of content, photo rights, branding, links, and responsive design, then merge the approved PR into `main`.
3. In repository **Settings → Pages**, choose **GitHub Actions** as the publishing source (one-time setting). Configure the `github-pages` environment's deployment protection rules where available.
4. A human uses **Actions → Publish approved LP to GitHub Pages → Run workflow**, chooses `main`, and checks **approved**. Changes pushed or merged to `main` alone do **not** publish.
5. The workflow re-runs lint/build, checks the exported `out/index.html`, uploads the `out/` artifact, and deploys via `actions/deploy-pages`. Verify the live Pages URL on mobile and desktop before sharing. Expected URL pattern (not proof of deployment): `https://suzu-0501.github.io/misemiru-lp-automation-test/`.

**Important:** This repository contains a fictional **Next.js test LP**, not customer LP artifacts. Future actual client LPs need a designated repository/publication target; never upload unapproved customer materials or assume that a local preview has been published.

## Safety and workflow
See `AGENTS.md` and `docs/`. The sample uses **no customer names, images, credentials, DM screenshots, or unconfirmed claims**.
`noindex,nofollow` is included for demonstration but **does not restrict access**. Public repositories and Pages are visible to third parties.

## Next steps
1. Complete per-client research and `requirements.md` privately; record sources, consent and unknowns.
2. Complete and critically review the `design-definition.md` before reference-image generation.
3. Approve usable images and their rights; edit in a feature branch with Codex.
4. Run QA, request independent review and only then merge/deploy. Customer outreach remains manual.
