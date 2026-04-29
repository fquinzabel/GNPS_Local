#!/usr/bin/env bash
# run.sh — start GNPS Local from WSL2
# Usage: bash run.sh
# Then open http://localhost:8000 in your Windows browser

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$SCRIPT_DIR"

# Activate conda env if available
if command -v conda &>/dev/null; then
  source "$(conda info --base)/etc/profile.d/conda.sh"
  conda activate gnps 2>/dev/null || echo "WARNING: gnps conda env not found, using current Python"
fi

echo ""
echo "  GNPS Local"
echo "  ────────────────────────────────"
echo "  Open in browser: http://localhost:8000"
echo "  Jobs stored in:  ~/gnps_jobs/"
echo "  Repo at:         $REPO_ROOT"
echo "  Stop with:       Ctrl+C"
echo ""

uvicorn app:app --host 0.0.0.0 --port 8000