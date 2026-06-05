#!/bin/bash
set -e

echo "==> Building package..."
python3 -m build

echo ""
echo "==> Creating isolated virtual environment..."
python3 -m venv /tmp/test-csc-translations
/tmp/test-csc-translations/bin/pip install --quiet dist/*.whl

echo ""
echo "==> Running smoke test against built dist..."
/tmp/test-csc-translations/bin/python - <<'EOF'
from countrystatecity_translations import (
    get_all_translations,
    get_translations_by_country,
    get_translations_by_language,
    get_translation,
    search_translations,
)

all_t = get_all_translations()
assert len(all_t) > 4000, "Expected 4000+ translations"
print(f"  get_all_translations()              -> {len(all_t)} entries")

de = get_translations_by_country("DE")
assert len(de) == 19
print(f"  get_translations_by_country(DE)     -> {len(de)} languages")

fr = get_translations_by_language("fr")
assert len(fr) > 100
print(f"  get_translations_by_language('fr')  -> {len(fr)} countries")

t = get_translation("DE", "fr")
assert t.translation == "Allemagne"
print(f"  get_translation(DE, fr)             -> {t.translation}")

results = search_translations("Allemagne")
assert len(results) > 0
print(f"  search_translations('Allemagne')    -> {len(results)} results")

print("")
print("All checks passed. Package is ready to publish.")
EOF

echo ""
echo "==> Cleaning up..."
rm -rf /tmp/test-csc-translations
