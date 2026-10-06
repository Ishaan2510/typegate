#!/usr/bin/env bash
# Rebuild the knowledge state from scratch (works in Git Bash on Windows, Linux, macOS).
# Usage: bash scripts/rebuild.sh            # uses the pinned commit below
#        PEPS_REF=main bash scripts/rebuild.sh   # rebuild against the latest PEPs
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PYTHON:-python}"
PEPS_REF="${PEPS_REF:-fc91a833f0d38d9aa95bee850a1301ec1c4bc3d4}"

if [ ! -d peps/.git ]; then
  git clone --depth 1 https://github.com/python/peps.git peps
fi
git -C peps fetch --depth 1 origin "$PEPS_REF"
git -C peps checkout -q FETCH_HEAD

"$PY" ingest/parse_peps.py --peps-dir peps/peps --out data/peps_raw.json
PEPS_COMMIT="$(git -C peps rev-parse HEAD)" "$PY" kg/build_graph.py
