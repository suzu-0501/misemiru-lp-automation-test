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
1. Review the PR and merge only after authorization.
2. In repository **Settings → Pages**, select **GitHub Actions** as the deployment source (may require a one-time manual setting).
3. On a push to `main`, `.github/workflows/pages.yml` builds and deploys the `out/` directory.
4. Verify the **actual** Pages URL on mobile and desktop before sharing. Expected URL pattern only (not yet deployed): `https://suzu-0501.github.io/misemiru-lp-automation-test/`.

## Safety and workflow
See `AGENTS.md` and `docs/`. The sample uses **no customer names, images, credentials, DM screenshots, or unconfirmed claims**.
`noindex,nofollow` is included for demonstration but **does not restrict access**. Public repositories and Pages are visible to third parties.

## Next steps
1. Complete per-client research and `requirements.md` privately; record sources, consent and unknowns.
2. Complete and critically review the `design-definition.md` before reference-image generation.
3. Approve usable images and their rights; edit in a feature branch with Codex.
4. Run QA, request independent review and only then merge/deploy. Customer outreach remains manual.
