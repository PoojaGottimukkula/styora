#!/usr/bin/env bash
set -euo pipefail

# Load local environment files if present. .env is loaded first, then .env.local to supplement or override.
for env_file in .env .env.local; do
  if [ -f "$env_file" ]; then
    echo "Loading env vars from $env_file"
    set -o allexport
    # shellcheck source=/dev/null
    source "$env_file"
    set +o allexport
  fi
done

# set_vercel_envs.sh
# Usage:
#   export VERCEL_TOKEN=... (personal token)
#   export VERCEL_PROJECT=styora
#   export WORKER_START_URL=https://your-worker-host/start
#   export WORKER_API_TOKEN=long-random-token
#   ./scripts/set_vercel_envs.sh

: ${VERCEL_TOKEN:?Need to set VERCEL_TOKEN}
: ${VERCEL_PROJECT:?Need to set VERCEL_PROJECT}
: ${WORKER_START_URL:?Need to set WORKER_START_URL}
: ${WORKER_API_TOKEN:?Need to set WORKER_API_TOKEN}

API_BASE="https://api.vercel.com/v9/projects"

# Create or update env var helper
set_env_var() {
  local key="$1"; local value="$2"; local target="$3"

  # Try to create
  resp=$(curl -sS -X POST "$API_BASE/$VERCEL_PROJECT/env" \
    -H "Authorization: Bearer $VERCEL_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"key\": \"$key\", \"value\": \"$value\", \"target\": [\"$target\"], \"type\": \"encrypted\"}") || true

  ok=$(echo "$resp" | python3 -c "import sys,json
try:
    print('ok' if json.load(sys.stdin).get('uid') else '')
except Exception:
    print('')") || true
  if [ -n "$ok" ]; then
    echo "Added $key to $VERCEL_PROJECT ($target)"
    return
  fi

  # If create failed, try to update existing var by listing and deleting then recreating
  list=$(curl -sS -H "Authorization: Bearer $VERCEL_TOKEN" "$API_BASE/$VERCEL_PROJECT/env")
  uids=$(echo "$list" | python3 -c "import sys,json
j=json.load(sys.stdin)
for e in j.get('envs',[]):
    if e.get('key')==sys.argv[1]:
        print(e.get('id'))
" "$key")
  for uid in $uids; do
    curl -sS -X DELETE -H "Authorization: Bearer $VERCEL_TOKEN" "$API_BASE/$VERCEL_PROJECT/env/$uid" >/dev/null
  done
  # recreate
  curl -sS -X POST "$API_BASE/$VERCEL_PROJECT/env" \
    -H "Authorization: Bearer $VERCEL_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"key\": \"$key\", \"value\": \"$value\", \"target\": [\"$target\"], \"type\": \"encrypted\"}" >/dev/null
  echo "Set $key on $VERCEL_PROJECT ($target)"
}

set_env_var WORKER_START_URL "$WORKER_START_URL" production
set_env_var WORKER_API_TOKEN "$WORKER_API_TOKEN" production

# Also set for preview and development if desired
set_env_var WORKER_START_URL "$WORKER_START_URL" preview
set_env_var WORKER_API_TOKEN "$WORKER_API_TOKEN" preview

set_env_var WORKER_START_URL "$WORKER_START_URL" development
set_env_var WORKER_API_TOKEN "$WORKER_API_TOKEN" development

echo "Vercel env vars set. Trigger a new deployment or re-deploy from the dashboard."
