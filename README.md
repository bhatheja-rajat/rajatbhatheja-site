# rajatbhatheja.is-a.dev

Personal brand site for **Rajat Bhatheja** — Data & AI Architect. Static, hosted on
Azure Static Web Apps, managed by an automation agent.

## How it works
- `content.json` — brand copy (source of truth).
- `posts.json` — featured essays, auto-pulled from The Data Muse (Substack RSS).
- `build_site.py` — deterministic renderer → `dist/index.html`.
- `site_posts_pull.py` — refresh `posts.json` from the Substack feed.
- Push to `main` → GitHub Action deploys `dist/` to Azure Static Web Apps.

## Update locally
```bash
python3 site_posts_pull.py      # optional: pull latest essays
python3 build_site.py           # render dist/index.html
git add -A && git commit -m "site: update" && git push
```
