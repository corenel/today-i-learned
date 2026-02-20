# Tooling Scripts

## `localize_markdown_images.py`

Find external markdown image links, download them into a markdown-sibling asset
directory, convert static images to WebP, and rewrite links to local paths.

Default mode is dry-run; use `--apply` to write changes.

Examples:

```bash
# Dry-run over all markdown files (recommended: uv ephemeral env)
uv run --with tqdm --with pillow --with requests python .tools/localize_markdown_images.py

# Apply changes for a single file
uv run --with tqdm --with pillow --with requests python .tools/localize_markdown_images.py --apply --include "weekly/2025/2025W11/README.zh-CN.md"

# Apply changes and emit a JSON report
uv run --with tqdm --with pillow --with requests python .tools/localize_markdown_images.py --apply --report-json .agents/localize-images/report.json

# If you prefer system Python, install dependencies first:
#   python -m pip install tqdm requests Pillow
# then run:
python .tools/localize_markdown_images.py --apply --include "weekly/2025/2025W11/README.zh-CN.md"
```

Key behavior:

- Scope defaults to `**/*.md` with safe excludes (`.git/**`, `.agents/**`, etc.).
- Assets are stored in `<markdown-stem>.assets/` next to each markdown file.
- Static raster images are converted to WebP.
- GIF/SVG are downloaded in original format (no transcoding).
- Idempotence uses `.image-localize-map.json` inside each asset directory.
- Progress uses `tqdm` on `stderr` (auto-enabled when `stderr` is a TTY); use `--progress` / `--no-progress` to override.
- Use `--verbose` for one compact per-file result line during processing.
