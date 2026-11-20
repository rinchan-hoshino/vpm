#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
chmod +x .githooks/* scripts/*.sh
git config core.hooksPath .githooks
echo "Git hooks enabled: $(git config --get core.hooksPath)"
