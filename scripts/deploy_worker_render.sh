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

# deploy_worker_render.sh
# Usage:
#   export RENDER_API_KEY=... (personal API key)
#   export GIT_REPO=owner/repo
#   export BRANCH=main
#   export SERVICE_NAME=styora-worker
#   export WORKER_API_TOKEN=long-random-token
#   export EMAIL_USER=you@example.com
#   export EMAIL_PASSWORD=secret
#   ./scripts/deploy_worker_render.sh

: ${RENDER_API_KEY:?Need to set RENDER_API_KEY}
: ${GIT_REPO:?Need to set GIT_REPO}
: ${BRANCH:=main}
: ${SERVICE_NAME:=styora-worker}
: ${WORKER_API_TOKEN:?Need to set WORKER_API_TOKEN}

EMAIL_USER=${EMAIL_USER:-}
EMAIL_PASSWORD=${EMAIL_PASSWORD:-}
EMAIL_FROM=${EMAIL_FROM:-}
PREVIEW_EMAIL=${PREVIEW_EMAIL:-}
AMAZON_ASSOCIATE_TAG=${AMAZON_ASSOCIATE_TAG:-}

API_URL="https://api.render.com/v1/services"

echo "Creating Render service: $SERVICE_NAME from repo $GIT_REPO (branch $BRANCH) ..."

read -r -d '' PAYLOAD <<EOF || true
{
  "service": {
    "name": "${SERVICE_NAME}",
    "repo": { "name": "${GIT_REPO}", "type": "github" },
    "branch": "${BRANCH}",
    "env": "python",
    "buildCommand": "",
    "startCommand": "python worker_server.py",
    "autoDeploy": true,
    "plan": "free"
  }
}
EOF

resp=$(curl -sS -X POST "$API_URL" \
  -H "Authorization: Bearer $RENDER_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

# Extract the service id and default domain
service_id=$(echo "$resp" | python3 -c "import sys, json
try:
    print(json.load(sys.stdin)['id'])
except Exception:
    sys.stderr.write('Failed to create service: '+json.dumps(json.loads('$resp')) if '$resp' else 'no response')") || true

if [ -z "$service_id" ] || [ "$service_id" = "None" ]; then
  echo "Failed to create Render service. Response:" >&2
  echo "$resp" >&2
  exit 1
fi

echo "Service created: $service_id"

# Set environment variables on the service
echo "Configuring environment variables..."

set_env() {
  local key="$1"; local val="$2"
  if [ -z "$val" ]; then
    return
  fi
  curl -sS -X POST "https://api.render.com/v1/services/${service_id}/env-vars" \
    -H "Authorization: Bearer $RENDER_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"key\": \"${key}\", \"value\": \"${val}\", \"secure\": true}" >/dev/null
}

set_env WORKER_API_TOKEN "$WORKER_API_TOKEN"
set_env EMAIL_USER "$EMAIL_USER"
set_env EMAIL_PASSWORD "$EMAIL_PASSWORD"
set_env EMAIL_FROM "$EMAIL_FROM"
set_env PREVIEW_EMAIL "$PREVIEW_EMAIL"
set_env AMAZON_ASSOCIATE_TAG "$AMAZON_ASSOCIATE_TAG"

echo "Environment variables configured (if provided)."

# Poll for the service's default domain
echo "Waiting for service to become available (this may take a minute)..."
for i in {1..30}; do
  info=$(curl -sS -H "Authorization: Bearer $RENDER_API_KEY" "https://api.render.com/v1/services/$service_id")
  domain=$(echo "$info" | python3 -c "import sys,json
try:
    j=json.load(sys.stdin)
    d=j.get('serviceDetails', {}) or j.get('defaultBranch', {}) or j
    print(j.get('defaultDomain') or j.get('serviceDetails', {}).get('defaultDomain','') or '')
except Exception:
    print('')")
  if [ -n "$domain" ]; then
    echo "Service domain: https://$domain"
    WORKER_URL="https://$domain"
    break
  fi
  sleep 4
done

if [ -z "${WORKER_URL:-}" ]; then
  echo "Could not determine service domain. Check Render dashboard." >&2
  exit 1
fi

echo "Render worker deployed at: $WORKER_URL"

echo "Next: run scripts/set_vercel_envs.sh to add WORKER_START_URL and WORKER_API_TOKEN to Vercel (requires VERCEL_TOKEN)."

echo "Done."
