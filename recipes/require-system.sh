#!/bin/bash
# Install the system packages (graphviz, npm) with the OS package
# manager, and uv when missing.

. ./tools/init-tracing.sh

case "$(uname -s)" in
  Linux)  which apt >/dev/null 2>&1 && sudo apt install -y graphviz npm \
          || printf "%s\n" "Non-Debian Linux: install graphviz and npm manually" ;;
  Darwin) which brew >/dev/null 2>&1 && brew install graphviz node uv \
          || printf "%s\n" "macOS without Homebrew: install graphviz, node and uv manually" ;;
  *)      echo "Unknown OS: install graphviz, node and uv manually" ;;
esac
which uv >/dev/null 2>&1 || curl -LsSf https://astral.sh/uv/install.sh | sh
