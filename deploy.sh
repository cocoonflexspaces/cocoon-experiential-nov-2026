#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────
# deploy.sh — push the Experiential holiday-activation proposal to GitHub Pages
#
# What this does:
#   1. Initializes a git repo in this folder (if not already)
#   2. Commits everything
#   3. Creates a NEW GitHub repo under your account
#   4. Pushes the deck
#   5. Enables GitHub Pages on the main branch
#   6. Prints the live URL
#
# Prerequisites:
#   • gh CLI installed and authenticated:  brew install gh && gh auth login
#   • git installed (default on macOS)
#
# Run from this folder:
#   bash deploy.sh
# ─────────────────────────────────────────────────────────────────────

set -euo pipefail

DEFAULT_REPO_NAME="cocoon-experiential-nov-2026"

# --- 0. Sanity ---
cd "$(dirname "$0")"

if ! command -v gh >/dev/null 2>&1; then
  echo "✗ gh CLI not installed."
  echo "  Install:  brew install gh"
  echo "  Then:     gh auth login"
  exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "✗ gh CLI is not authenticated."
  echo "  Run:  gh auth login"
  exit 1
fi

# --- 1. Pick a repo name ---
read -rp "Repository name [${DEFAULT_REPO_NAME}]: " REPO_NAME
REPO_NAME="${REPO_NAME:-$DEFAULT_REPO_NAME}"

# --- 2. Init git if needed ---
if [ ! -d .git ]; then
  echo "→ Initializing git repo…"
  git init -q
  git checkout -b main 2>/dev/null || git checkout main
fi

# --- 3. Stage + commit ---
echo "→ Staging files…"
git add -A
if ! git diff --cached --quiet; then
  git commit -q -m "Experiential holiday activation proposal update · $(date +%Y-%m-%d)"
fi

# --- 4. Create remote repo ---
GH_USER="cocoonflexspaces"
echo "→ Creating GitHub repo:  ${GH_USER}/${REPO_NAME}  (private)"

if gh repo view "${GH_USER}/${REPO_NAME}" >/dev/null 2>&1; then
  echo "  Repo already exists — reusing."
else
  gh repo create "cocoonflexspaces/${REPO_NAME}" --private --source=. --remote=origin --push -y
fi

if ! git remote get-url origin >/dev/null 2>&1; then
  git remote add origin "https://github.com/${GH_USER}/${REPO_NAME}.git"
fi

# --- 5. Push ---
echo "→ Pushing to main…"
git push -u origin main -q

# --- 6. Enable Pages ---
echo "→ Enabling GitHub Pages…"
VISIBILITY="$(gh repo view "${GH_USER}/${REPO_NAME}" --json visibility --jq .visibility)"
if [ "$VISIBILITY" = "PRIVATE" ]; then
  read -rp "  GitHub Pages requires a public repo on free plans. Make this repo public? [y/N] " MK
  if [[ "$MK" =~ ^[Yy]$ ]]; then
    gh repo edit "${GH_USER}/${REPO_NAME}" --visibility public --accept-visibility-change-consequences
  else
    echo "  Repo left private. Pages won't be enabled — share the repo URL instead."
    echo "  Repo:  https://github.com/${GH_USER}/${REPO_NAME}"
    exit 0
  fi
fi

gh api -X POST "/repos/${GH_USER}/${REPO_NAME}/pages" \
  -f "source[branch]=main" \
  -f "source[path]=/" >/dev/null 2>&1 || \
gh api -X PUT "/repos/${GH_USER}/${REPO_NAME}/pages" \
  -f "source[branch]=main" \
  -f "source[path]=/" >/dev/null 2>&1 || true

URL="https://${GH_USER}.github.io/${REPO_NAME}/"

echo ""
echo "──────────────────────────────────────────────────────────────"
echo "  ✓ Deck deployed."
echo ""
echo "  Live URL:  ${URL}"
echo "  Repo:      https://github.com/${GH_USER}/${REPO_NAME}"
echo ""
echo "  GitHub Pages takes ~30–90 seconds to build the first time."
echo "  If the URL 404s for a minute, give it a moment and retry."
echo "──────────────────────────────────────────────────────────────"
