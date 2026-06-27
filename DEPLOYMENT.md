# Deployment

## Architecture

This project is split into two deployable pieces:

1. Vercel web dashboard
   - Serves `public/index.html`.
   - Shows a Start Workflow button.
   - Calls `/api/start` when the button is clicked.

2. Persistent worker
   - Runs `worker_server.py`.
   - Receives `/start` from Vercel.
   - Starts `main.py`, which runs the Selenium Amazon and Instagram workflow.

The Selenium bot should not run inside a Vercel Function. The bot needs a persistent browser profile and a long-running approval monitor, while Vercel Functions are request-based and time-limited.

Use Vercel for the button UI. Use a persistent worker host such as Render, Railway, Fly.io, a VPS, or a small cloud VM for the actual bot.

## Vercel Setup

Deploy this repository to Vercel. The dashboard is available at:

- `/`
- `/health`

Set these Vercel environment variables:

```bash
WORKER_START_URL=https://your-worker.example.com/start
WORKER_API_TOKEN=use-a-long-random-token
```

The token is optional in code, but recommended.

## Worker Setup

Deploy the same repository to a persistent worker host and run:

```bash
python worker_server.py
```

Many hosts can also use the included `Procfile`:

```bash
web: python worker_server.py
```

The worker must have Chrome or a supported browser installed for Selenium.

## Required Environment Variables

Set these in Vercel or in your worker host. Do not commit real values.

```bash
EMAIL_FROM=
EMAIL_USER=
EMAIL_PASSWORD=
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
PREVIEW_EMAIL=
AMAZON_ASSOCIATE_TAG=
AFFILIATE_SHORTENER_API=
WORKER_API_TOKEN=
```

Short-link behavior:
- Existing Amazon short links such as `https://amzn.to/...` are preserved as-is.
- The app does not fabricate new `amzn.to` links from a plain URL template; creating them usually requires Amazon Associates/SiteStripe or another service that can issue `amzn.to` links.

## GitHub Hygiene

The following are ignored by `.gitignore` and should not be committed:

- `.env` files
- `venv/`
- `chrome_profile/`
- `approvals/`
- `images/`
- `product_links.txt`
- Python cache files

If any secret was previously committed, rotate it immediately and remove it from Git history before pushing to GitHub.

## Local Worker Command

To run the bot directly without the web dashboard:

```bash
python main.py
```

To run the worker API locally:

```bash
python worker_server.py
```
