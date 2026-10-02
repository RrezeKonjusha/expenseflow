#!/usr/bin/env bash
# Builds the single documentation PDF: build/ExpenseFlow-documentation.pdf
#   scripts/build-docs.sh
# Needs pandoc 3, Node 20+ and Google Chrome (CHROME_PATH to override). The PDF is a release asset, not committed.
set -euo pipefail
cd "$(dirname "$0")/.."

OUT=build
VERSION=$(git describe --tags --always 2>/dev/null || echo dev)
TODAY=$(date '+%d %B %Y')
mkdir -p "$OUT"

# Order of the book; every file is one chapter.
DOCS=(
  docs/srs.md
  docs/phase-1.md
  docs/design.md
  docs/modules/accounts.md docs/modules/users.md docs/modules/expenses.md docs/modules/reporting.md docs/modules/core.md
  docs/test-report.md
  docs/production-readiness.md
  docs/deployment.md
  docs/maintenance.md
  docs/user-manual.md
  docs/project-management.md
)

sed -e "s/{{VERSION}}/$VERSION/" -e "s/{{DATE}}/$TODAY/" scripts/docs/title.html > "$OUT/title.html"

pandoc "${DOCS[@]}" \
  --from gfm --to html5 --standalone --embed-resources \
  --resource-path=docs \
  --toc --toc-depth=2 \
  --css scripts/docs/print.css \
  --include-before-body "$OUT/title.html" \
  --metadata pagetitle="ExpenseFlow documentation" \
  --output "$OUT/ExpenseFlow-documentation.html"

[ -d scripts/docs/node_modules/puppeteer-core ] ||
  (cd scripts/docs && npm install --no-save --no-package-lock --silent puppeteer-core@24)
node scripts/docs/print-pdf.mjs "$OUT/ExpenseFlow-documentation.html" "$OUT/ExpenseFlow-documentation.pdf"
