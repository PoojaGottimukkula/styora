Render deployment steps (worker)

1. Create the Render web service

- Go to https://dashboard.render.com and sign in.
- Click "New" → "Web Service" → Connect your repository (GitHub/GitLab).
- For "Name" use `styora-worker`.
- Branch: `main` (or the branch you deploy from).
- Environment: `Python`.
- Build Command: leave empty (Render will install from `requirements.txt`).
- Start Command: `python worker_server.py`.
- Region: pick nearest region.
- Click "Create Web Service".

2. Add required environment variables (Render Dashboard, Service Settings → Environment)
- EMAIL_FROM
- EMAIL_USER
- EMAIL_PASSWORD (mark as secret)
- EMAIL_HOST (smtp.gmail.com)
- EMAIL_PORT (587)
- EMAIL_USE_TLS (true)
- PREVIEW_EMAIL
- AMAZON_ASSOCIATE_TAG
- WORKER_API_TOKEN (mark as secret)

3. After deployment, note the service URL (e.g. https://styora-worker.onrender.com).

4. Configure Vercel (dashboard or CLI)
- Add the following environment variables to your Vercel project `styora` (Project Settings → Environment Variables):
  - WORKER_START_URL = https://<your-worker-host>/start
  - WORKER_API_TOKEN = <same token you set on Render>

CLI example (interactive):

```bash
# set the worker start URL (production)
npx vercel env add WORKER_START_URL production
# paste the full URL when prompted

# set the worker token
npx vercel env add WORKER_API_TOKEN production
# paste the token (secret) when prompted
```

5. Verify

- Check worker health:

```bash
curl -i https://<your-worker-host>/health
```

- Trigger start via Vercel dashboard Start button or directly:

```bash
curl -i -X POST https://<your-vercel-site>/api/start
```

The Vercel `/api/start` route will forward the request to the worker (it includes the `Authorization` header if `WORKER_API_TOKEN` is configured).

6. Troubleshooting

- If Vercel returns 502 when forwarding, verify `WORKER_START_URL` is correct and reachable from the public internet.
- Check Render service logs for startup errors.
- Ensure `EMAIL_*` values are present on the worker host if email previews are required.
