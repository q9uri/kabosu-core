# ライセンス一覧を生成する

set -eux

uv run python tools/generate_licenses.py > resources/engine_manifest_assets/dependency_licenses.json
