#!/usr/bin/env python3
"""Localize external markdown image links to in-repo assets.

This script finds external image links in markdown files, downloads them into a
markdown-sibling asset folder, converts static raster images to WebP, preserves
GIF/SVG in original format, and rewrites markdown image URLs to local relative
paths.

Default behavior is dry-run. Use --apply to write files.

Recommended invocation (no global installs):
  uv run --with pillow --with requests python .tools/localize_markdown_images.py --apply

Fallback with system Python:
  python -m pip install requests Pillow
  python .tools/localize_markdown_images.py --apply
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import fnmatch
import hashlib
import json
import os
import re
import sys
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple
from urllib.parse import parse_qs, urlparse


IMAGE_LINK_START = "!["
# Match markdown fenced-code delimiters; links inside fences are intentionally
# ignored to avoid mutating example snippets.
FENCE_RE = re.compile(r"^\s*(```|~~~)")
FILENAME_INDEX_RE = r"^{stem}_(\d+)\.[^.]+$"

DEFAULT_INCLUDE = ["**/*.md"]
DEFAULT_EXCLUDE = [
    ".git/**",
    ".agents/**",
    ".venv/**",
    "**/__pycache__/**",
]

EXTENSION_ALIASES = {
    "jpg": ".jpg",
    "jpeg": ".jpg",
    "png": ".png",
    "gif": ".gif",
    "svg": ".svg",
    "svg+xml": ".svg",
    "webp": ".webp",
    "bmp": ".bmp",
    "tif": ".tif",
    "tiff": ".tif",
    "avif": ".avif",
}

PASSTHROUGH_EXTENSIONS = {".gif", ".svg"}


@dataclass
class Config:
    """Execution options resolved from CLI arguments.

    Attributes:
        root: Repository root used for discovery and relative-path rendering.
        apply: Whether to mutate markdown/assets (`False` means dry-run only).
        include: Glob patterns used to discover markdown files.
        exclude: Glob patterns filtered out after include matching.
        strict: Whether to stop on first per-file/per-URL error.
        quality: WebP lossy quality parameter in `[0, 100]`.
        method: WebP encoder effort parameter in `[0, 6]`.
        metadata_name: Per-markdown metadata filename under the asset directory.
        report_json: Optional JSON report destination path.
    """

    root: Path
    apply: bool
    include: List[str]
    exclude: List[str]
    strict: bool
    quality: int
    method: int
    metadata_name: str
    report_json: Optional[Path]


@dataclass
class FileResult:
    """Aggregated processing outcome for one markdown file.

    Attributes:
        markdown_path: Markdown path relative to repository root.
        image_links_found: Number of external image link matches discovered.
        rewritten_links: Number of markdown image links rewritten to local paths.
        reused_urls: Number of URLs resolved from existing metadata/files.
        planned_urls: Number of URLs planned in dry-run mode.
        downloaded_urls: Number of URLs materialized in apply mode.
        would_change: Whether rewritten markdown differs from original text.
        wrote_markdown: Whether markdown file content was written.
        wrote_metadata: Whether metadata JSON was written.
        resolved_urls: Map of external URL to local relative asset path.
        errors: Collected error messages for this markdown file.
    """

    markdown_path: str
    image_links_found: int = 0
    rewritten_links: int = 0
    reused_urls: int = 0
    planned_urls: int = 0
    downloaded_urls: int = 0
    would_change: bool = False
    wrote_markdown: bool = False
    wrote_metadata: bool = False
    resolved_urls: Dict[str, str] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)


@dataclass
class ResolveResult:
    """Resolution result for one external image URL.

    Attributes:
        relative_path: Markdown-relative localized path to inject.
        status: Resolution mode: `reused`, `planned`, or `downloaded`.
    """

    relative_path: str
    status: str  # reused | planned | downloaded


@dataclass(frozen=True)
class ExternalImageMatch:
    """Parsed markdown image link match for an external HTTP(S) URL.

    Attributes:
        start: Inclusive start offset in markdown content.
        end: Exclusive end offset in markdown content.
        full_text: Original markdown slice that was matched.
        alt: Markdown image alt text between `[` and `]`.
        url: External HTTP(S) image URL captured from link destination.
        title: Optional markdown image title, including leading whitespace and
            surrounding quotes, or empty string when absent.
    """

    start: int
    end: int
    full_text: str
    alt: str
    url: str
    title: str


def parse_args() -> Config:
    """Parse and validate CLI arguments into a normalized config object.

    Returns:
        A validated ``Config`` instance with default include/exclude patterns.

    Raises:
        SystemExit: If any parser validation fails or numeric bounds are invalid.
    """

    parser = argparse.ArgumentParser(
        description=(
            "Localize external markdown image links into local assets and "
            "convert static images to WebP."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  uv run --with pillow --with requests python .tools/localize_markdown_images.py\n"
            "  uv run --with pillow --with requests python .tools/localize_markdown_images.py --apply\n"
            "  python .tools/localize_markdown_images.py --apply  # when deps are installed in system env\n"
        ),
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Repository root. Default: current directory.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write markdown/assets/metadata. Default is dry-run.",
    )
    parser.add_argument(
        "--include",
        action="append",
        default=[],
        help="Include glob pattern. Repeatable. Default: **/*.md",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Exclude glob pattern. Repeatable.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail fast on first processing error.",
    )
    parser.add_argument(
        "--quality",
        type=int,
        default=82,
        help="WebP quality for lossy conversion. Default: 82.",
    )
    parser.add_argument(
        "--method",
        type=int,
        default=6,
        help="WebP encoder method 0..6. Default: 6.",
    )
    parser.add_argument(
        "--metadata-name",
        default=".image-localize-map.json",
        help="Metadata filename stored under each markdown asset directory.",
    )
    parser.add_argument(
        "--report-json",
        type=Path,
        default=None,
        help="Optional path for JSON report output.",
    )
    args = parser.parse_args()

    if not 0 <= args.quality <= 100:
        print("error: --quality must be in [0, 100]", file=sys.stderr)
        raise SystemExit(2)
    if not 0 <= args.method <= 6:
        print("error: --method must be in [0, 6]", file=sys.stderr)
        raise SystemExit(2)

    include = args.include if args.include else list(DEFAULT_INCLUDE)
    exclude = list(DEFAULT_EXCLUDE) + list(args.exclude)

    return Config(
        root=args.root.resolve(),
        apply=bool(args.apply),
        include=include,
        exclude=exclude,
        strict=bool(args.strict),
        quality=int(args.quality),
        method=int(args.method),
        metadata_name=str(args.metadata_name),
        report_json=args.report_json.resolve() if args.report_json else None,
    )


def create_http_session():
    """Create an HTTP session with retry policy compatible across urllib3 versions.

    Returns:
        requests.Session: Session configured with retries and a stable User-Agent.
    """

    import inspect

    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry

    retry_kwargs = {
        "total": 3,
        "connect": 3,
        "read": 3,
        "backoff_factor": 0.5,
        "status_forcelist": [429, 500, 502, 503, 504],
    }
    # urllib3 renamed this parameter in newer versions. Support both names so
    # the script works in system Python and ephemeral uv environments.
    init_params = set(inspect.signature(Retry.__init__).parameters)
    if "allowed_methods" in init_params:
        retry_kwargs["allowed_methods"] = frozenset({"GET", "HEAD"})
    elif "method_whitelist" in init_params:
        retry_kwargs["method_whitelist"] = frozenset({"GET", "HEAD"})

    retries = Retry(**retry_kwargs)
    adapter = HTTPAdapter(max_retries=retries)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update({"User-Agent": "til-image-localizer/1.0"})
    return session


def ensure_apply_dependencies() -> None:
    """Ensure runtime dependencies for ``--apply`` mode are importable.

    Raises:
        SystemExit: If ``requests`` and/or ``Pillow`` are missing.
    """

    missing: List[str] = []
    try:
        import requests  # noqa: F401
    except Exception:
        missing.append("requests")
    try:
        import PIL  # noqa: F401
    except Exception:
        missing.append("Pillow")
    if missing:
        joined = ", ".join(missing)
        print(
            f"error: missing dependencies for --apply: {joined}. "
            "Run with uv ephemeral deps:\n"
            "  uv run --with pillow --with requests python .tools/localize_markdown_images.py --apply\n"
            f"Or install in current Python env: pip install {joined}",
            file=sys.stderr,
        )
        raise SystemExit(2)


def to_posix_relative(path: Path, start: Path) -> str:
    """Return a POSIX-style relative path for cross-platform markdown output.

    Args:
        path: Path to convert.
        start: Base directory used for ``relpath``.

    Returns:
        Forward-slash relative path string.
    """

    return Path(os.path.relpath(path, start=start)).as_posix()


def discover_markdown_files(root: Path, include: Sequence[str], exclude: Sequence[str]) -> List[Path]:
    """Discover markdown files from include/exclude glob rules.

    Args:
        root: Repository root directory.
        include: Include patterns evaluated from ``root``.
        exclude: Exclude patterns evaluated against repository-relative paths.

    Returns:
        Sorted list of unique markdown paths.
    """

    matched: Dict[str, Path] = {}
    for pattern in include:
        for path in root.glob(pattern):
            if not path.is_file():
                continue
            rel = to_posix_relative(path, root)
            if should_exclude(rel, exclude):
                continue
            matched[rel] = path
    return [matched[key] for key in sorted(matched)]


def should_exclude(relative_path: str, exclude_patterns: Sequence[str]) -> bool:
    """Check whether a relative path matches any exclusion pattern.

    Args:
        relative_path: Path rendered relative to repository root.
        exclude_patterns: Glob patterns to test.

    Returns:
        ``True`` when the path should be excluded from processing.
    """

    rel = relative_path
    return any(fnmatch.fnmatch(rel, pattern) for pattern in exclude_patterns)


def fenced_ranges(content: str) -> List[Tuple[int, int]]:
    """Return character-index ranges occupied by fenced code blocks.

    Args:
        content: Full markdown text.

    Returns:
        List of inclusive-start/exclusive-end character ranges.

    Note:
        This is line-oriented and intentionally lightweight; it is sufficient for
        this repository's markdown style and avoids adding a full markdown parser.
    """

    lines = content.splitlines(keepends=True)
    ranges: List[Tuple[int, int]] = []
    in_fence = False
    offset = 0
    start = 0

    for line in lines:
        if FENCE_RE.match(line):
            if not in_fence:
                in_fence = True
                start = offset
            else:
                ranges.append((start, offset + len(line)))
                in_fence = False
        offset += len(line)

    if in_fence:
        ranges.append((start, len(content)))
    return ranges


def in_ranges(index: int, ranges: Sequence[Tuple[int, int]]) -> bool:
    """Determine whether a character index falls in any sorted range.

    Args:
        index: Character offset in the original content.
        ranges: Sorted start/end range pairs.

    Returns:
        ``True`` if ``index`` is inside one of the ranges.
    """

    for start, end in ranges:
        # Early exit keeps this linear scan cheap for common markdown sizes.
        if index < start:
            return False
        if start <= index < end:
            return True
    return False


def find_unescaped_char(content: str, start: int, target: str) -> int:
    """Find the next unescaped target character from ``start``.

    Args:
        content: Full markdown content.
        start: Search start index.
        target: Single-character token to locate.

    Returns:
        Character index of the first unescaped target, or ``-1`` when missing.
    """

    escaped = False
    for index in range(start, len(content)):
        char = content[index]
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == target:
            return index
    return -1


def parse_optional_image_title(content: str, start: int) -> Tuple[Optional[str], int]:
    """Parse optional markdown image title that follows a link destination.

    Args:
        content: Full markdown content.
        start: Index expected to be at whitespace before a title.

    Returns:
        Tuple of parsed title slice (or empty string when absent) and next index.
        Returns ``(None, start)`` when title-like syntax is malformed.
    """

    cursor = start
    while cursor < len(content) and content[cursor].isspace():
        cursor += 1

    if cursor == start:
        return "", start
    if cursor >= len(content) or content[cursor] not in {'"', "'"}:
        return None, start

    quote = content[cursor]
    cursor += 1

    while cursor < len(content):
        char = content[cursor]
        if char == "\\":
            cursor += 2
            continue
        if char == quote:
            return content[start : cursor + 1], cursor + 1
        cursor += 1

    return None, start


def parse_external_image_link_at(content: str, start: int) -> Optional[ExternalImageMatch]:
    """Parse a markdown image link at an exact offset.

    Args:
        content: Full markdown content.
        start: Expected offset of an image link beginning with `![`.

    Returns:
        ``ExternalImageMatch`` when the syntax is a supported external HTTP(S)
        markdown image link, otherwise ``None``.
    """

    if not content.startswith(IMAGE_LINK_START, start):
        return None

    alt_start = start + len(IMAGE_LINK_START)
    alt_end = find_unescaped_char(content, alt_start, "]")
    if alt_end < 0:
        return None
    if alt_end + 1 >= len(content) or content[alt_end + 1] != "(":
        return None

    cursor = alt_end + 2
    url_start = cursor
    if not (
        content.startswith("http://", url_start)
        or content.startswith("https://", url_start)
    ):
        return None

    paren_depth = 0
    while cursor < len(content):
        char = content[cursor]
        if char == "\\":
            cursor += 2
            continue
        if char.isspace() and paren_depth == 0:
            break
        if char == "(":
            paren_depth += 1
            cursor += 1
            continue
        if char == ")":
            if paren_depth == 0:
                break
            paren_depth -= 1
            cursor += 1
            continue
        cursor += 1

    if cursor == url_start or paren_depth != 0:
        return None

    url = content[url_start:cursor]
    title = ""
    if cursor < len(content) and content[cursor].isspace():
        parsed_title, next_cursor = parse_optional_image_title(content, cursor)
        if parsed_title is None:
            return None
        title = parsed_title
        cursor = next_cursor

    if cursor >= len(content) or content[cursor] != ")":
        return None

    end = cursor + 1
    return ExternalImageMatch(
        start=start,
        end=end,
        full_text=content[start:end],
        alt=content[alt_start:alt_end],
        url=url,
        title=title,
    )


def iter_external_image_matches(content: str) -> Iterable[ExternalImageMatch]:
    """Yield external markdown image links outside fenced code blocks.

    Args:
        content: Full markdown content to scan.

    Yields:
        Parsed matches for supported external markdown image syntax.
    """

    ranges = fenced_ranges(content)
    cursor = 0
    while True:
        start = content.find(IMAGE_LINK_START, cursor)
        if start < 0:
            break
        cursor = start + len(IMAGE_LINK_START)
        if in_ranges(start, ranges):
            continue
        match = parse_external_image_link_at(content, start)
        if match is None:
            continue
        yield match
        cursor = max(cursor, match.end)


def rewrite_markdown_with_mapping(
    content: str, url_to_relative: Mapping[str, str]
) -> Tuple[str, int]:
    """Rewrite markdown image URLs according to a URL-to-local mapping.

    Args:
        content: Original markdown content.
        url_to_relative: Mapping from external URL to localized relative path.

    Returns:
        Tuple of rewritten content and number of links actually rewritten.
    """

    replacements: List[Tuple[int, int, str]] = []
    rewritten = 0

    for match in iter_external_image_matches(content):
        url = match.url
        if url not in url_to_relative:
            continue
        alt = match.alt
        title = match.title
        replacement = f"![{alt}]({url_to_relative[url]}{title})"
        replacements.append((match.start, match.end, replacement))
        if replacement != match.full_text:
            rewritten += 1

    if not replacements:
        return content, 0

    chunks: List[str] = []
    cursor = 0
    # Rebuild from stable spans to avoid offset drift while replacing many links.
    for start, end, replacement in replacements:
        chunks.append(content[cursor:start])
        chunks.append(replacement)
        cursor = end
    chunks.append(content[cursor:])

    return "".join(chunks), rewritten


def guess_extension_from_content_type(content_type: str) -> Optional[str]:
    """Infer file extension from HTTP content type.

    Args:
        content_type: Raw ``Content-Type`` header value.

    Returns:
        Normalized extension (including dot) or ``None`` if unsupported/unknown.
    """

    if not content_type:
        return None
    content_type = content_type.split(";", 1)[0].strip().lower()
    if not content_type.startswith("image/"):
        return None
    raw = content_type[len("image/") :]
    return EXTENSION_ALIASES.get(raw)


def guess_extension_from_url(url: str) -> Optional[str]:
    """Infer extension from URL query hints and path suffix.

    Args:
        url: External URL from markdown image link.

    Returns:
        Normalized extension (including dot) or ``None``.

    Note:
        Query `format=` hints are checked first because many hosts (for example,
        image CDNs) expose extension-like format only in query parameters.
    """

    parsed = urlparse(url)
    query = parse_qs(parsed.query)

    format_hint = query.get("format", [])
    if format_hint:
        raw = format_hint[0].strip().lower().lstrip(".")
        ext = EXTENSION_ALIASES.get(raw)
        if ext:
            return ext

    suffix = Path(parsed.path).suffix.strip().lower()
    if suffix.startswith("."):
        ext = EXTENSION_ALIASES.get(suffix[1:], suffix)
        if ext in {".jpg", ".png", ".gif", ".svg", ".webp", ".bmp", ".tif", ".avif"}:
            return ext
    return None


def parse_existing_index(filename: str, stem: str) -> Optional[int]:
    """Parse sequential asset index from an existing localized filename.

    Args:
        filename: Candidate asset filename.
        stem: Markdown stem used in naming convention.

    Returns:
        Parsed integer index, or ``None`` when pattern does not match.
    """

    pattern = re.compile(FILENAME_INDEX_RE.format(stem=re.escape(stem)))
    match = pattern.match(filename)
    if not match:
        return None
    try:
        return int(match.group(1))
    except ValueError:
        return None


def next_index_start(asset_dir: Path, metadata: Mapping[str, object], stem: str) -> int:
    """Compute the next filename index for a markdown's asset directory.

    Args:
        asset_dir: Asset directory path for one markdown file.
        metadata: Loaded metadata map containing prior localized paths.
        stem: Markdown stem used in naming convention.

    Returns:
        Next 1-based index to use when allocating new asset filenames.
    """

    indexes: List[int] = []

    for value in metadata.values():
        if not isinstance(value, dict):
            continue
        relative_path = value.get("relative_path")
        if not isinstance(relative_path, str):
            continue
        idx = parse_existing_index(Path(relative_path).name, stem)
        if idx is not None:
            indexes.append(idx)

    if asset_dir.exists():
        for path in asset_dir.iterdir():
            if not path.is_file():
                continue
            # Scan disk to stay robust if metadata was removed or out-of-date.
            idx = parse_existing_index(path.name, stem)
            if idx is not None:
                indexes.append(idx)

    return (max(indexes) + 1) if indexes else 1


def load_metadata(metadata_path: Path) -> Dict[str, Dict[str, object]]:
    """Load and normalize per-markdown localization metadata.

    Args:
        metadata_path: Metadata JSON file path.

    Returns:
        URL-keyed mapping. Invalid/malformed payloads degrade to empty map.
    """

    if not metadata_path.exists():
        return {}
    try:
        raw = json.loads(metadata_path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    if not isinstance(raw, dict):
        return {}

    normalized: Dict[str, Dict[str, object]] = {}
    for key, value in raw.items():
        if isinstance(key, str) and isinstance(value, dict):
            normalized[key] = dict(value)
    return normalized


def write_json(path: Path, payload: object) -> None:
    """Write UTF-8 JSON with deterministic formatting and trailing newline.

    Args:
        path: Destination path.
        payload: JSON-serializable object.
    """

    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
    path.write_text(text + "\n", encoding="utf-8")


def utc_now_iso() -> str:
    """Return timezone-aware UTC timestamp in ISO-8601 format."""

    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def classify_storage_mode(
    downloaded_file: Path, url: str, content_type: str
) -> Tuple[str, str]:
    """Decide whether to pass through original bytes or transcode to WebP.

    Args:
        downloaded_file: Temporary downloaded payload path.
        url: Source URL, used for fallback hinting and diagnostics.
        content_type: HTTP content type for the downloaded payload.

    Returns:
        Tuple ``(mode, extension)`` where mode is ``passthrough`` or ``webp``.

    Raises:
        ValueError: If the payload cannot be identified as supported image input.
    """

    hinted_ext = guess_extension_from_content_type(content_type) or guess_extension_from_url(url)
    if hinted_ext in PASSTHROUGH_EXTENSIONS:
        return ("passthrough", hinted_ext)

    from PIL import Image, UnidentifiedImageError

    try:
        with Image.open(downloaded_file) as image:
            fmt = (image.format or "").strip().lower()
            if fmt == "gif":
                return ("passthrough", ".gif")
            # Keep WebP as-is to avoid generation-loss from unnecessary re-encode.
            if fmt == "webp":
                return ("passthrough", ".webp")
            if fmt in {"jpeg", "jpg", "png", "bmp", "tiff", "avif"}:
                return ("webp", ".webp")
    except UnidentifiedImageError as exc:
        if hinted_ext == ".svg":
            return ("passthrough", ".svg")
        raise ValueError(f"Unsupported or invalid image payload: {url}") from exc

    if hinted_ext == ".svg":
        return ("passthrough", ".svg")
    raise ValueError(f"Unable to classify downloaded image payload: {url}")


def convert_to_webp(
    source_path: Path, target_tmp_path: Path, quality: int, method: int
) -> None:
    """Convert image payload to WebP with EXIF orientation normalization.

    Args:
        source_path: Source image path.
        target_tmp_path: Destination temporary path for encoded WebP.
        quality: WebP quality value in `[0, 100]`.
        method: WebP encoder effort in `[0, 6]`.
    """

    from PIL import Image, ImageOps

    with Image.open(source_path) as image:
        # Normalize orientation before conversion so markdown viewers display
        # consistent results regardless of EXIF-aware rendering differences.
        image = ImageOps.exif_transpose(image)
        if image.mode not in {"RGB", "RGBA"}:
            if "A" in image.getbands():
                image = image.convert("RGBA")
            else:
                image = image.convert("RGB")
        image.save(
            target_tmp_path,
            format="WEBP",
            quality=quality,
            method=method,
            optimize=True,
        )


def download_binary(session, url: str, target_path: Path) -> Tuple[str, str]:
    """Download URL bytes to disk while computing a SHA-256 digest.

    Args:
        session: Configured HTTP session.
        url: Source URL.
        target_path: Temporary destination path.

    Returns:
        Tuple of normalized response content type and SHA-256 hex digest.

    Raises:
        requests.RequestException: On network/HTTP errors.
        ValueError: If zero bytes are downloaded.
    """

    with session.get(url, timeout=(5, 30), stream=True) as response:
        response.raise_for_status()
        content_type = response.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
        hasher = hashlib.sha256()
        bytes_written = 0
        with target_path.open("wb") as handle:
            for chunk in response.iter_content(chunk_size=65536):
                if not chunk:
                    continue
                handle.write(chunk)
                hasher.update(chunk)
                bytes_written += len(chunk)
    if bytes_written == 0:
        raise ValueError(f"Downloaded empty payload: {url}")
    return content_type, hasher.hexdigest()


def materialize_url(
    *,
    session,
    url: str,
    asset_dir: Path,
    stem: str,
    index: int,
    quality: int,
    method: int,
) -> Tuple[str, str, str, str]:
    """Download and store one URL into the markdown asset directory.

    Args:
        session: Configured HTTP session.
        url: External image URL.
        asset_dir: Target asset directory for the owning markdown file.
        stem: Markdown stem used for filename generation.
        index: Numeric index for deterministic filename allocation.
        quality: WebP quality for transcodes.
        method: WebP encoder method for transcodes.

    Returns:
        Tuple of filename, stored format, source content type, and SHA-256 hash.

    Note:
        Writes are staged via temporary files and finalized with ``os.replace``
        to preserve atomicity on interruption.
    """

    asset_dir.mkdir(parents=True, exist_ok=True)
    download_path = asset_dir / f".download-{uuid.uuid4().hex}"
    write_tmp = asset_dir / f".write-{uuid.uuid4().hex}"

    try:
        content_type, digest = download_binary(session=session, url=url, target_path=download_path)
        mode, ext = classify_storage_mode(downloaded_file=download_path, url=url, content_type=content_type)
        filename = f"{stem}_{index:03d}{ext if mode == 'passthrough' else '.webp'}"
        final_path = asset_dir / filename

        if mode == "passthrough":
            # Keep original bytes/format (for example gif/svg/webp).
            os.replace(download_path, write_tmp)
            os.replace(write_tmp, final_path)
            stored_format = ext.lstrip(".")
        else:
            convert_to_webp(
                source_path=download_path,
                target_tmp_path=write_tmp,
                quality=quality,
                method=method,
            )
            os.replace(write_tmp, final_path)
            stored_format = "webp"

        return filename, stored_format, content_type, digest
    finally:
        if download_path.exists():
            download_path.unlink()
        if write_tmp.exists():
            write_tmp.unlink()


def resolve_url_for_markdown(
    *,
    config: Config,
    session,
    markdown_path: Path,
    url: str,
    metadata: Dict[str, Dict[str, object]],
    asset_dir: Path,
    stem: str,
    next_index_ref: List[int],
) -> ResolveResult:
    """Resolve one external URL to a local relative asset path.

    Args:
        config: Run configuration.
        session: Optional HTTP session (required in apply mode).
        markdown_path: Markdown file owning this link.
        url: External image URL.
        metadata: Mutable metadata map for this markdown file.
        asset_dir: Local asset directory for this markdown file.
        stem: Markdown stem used in local naming convention.
        next_index_ref: Single-item list used as mutable index counter.

    Returns:
        ``ResolveResult`` with resolved relative path and resolution status.

    Raises:
        Exception: Propagates download/format/write exceptions in apply mode.
    """

    existing = metadata.get(url) if isinstance(metadata.get(url), dict) else None
    if existing:
        relative_path = existing.get("relative_path")
        if isinstance(relative_path, str):
            existing_abs = markdown_path.parent / Path(relative_path)
            if existing_abs.exists():
                return ResolveResult(
                    relative_path=relative_path,
                    status="reused",
                )

    index: Optional[int] = None
    if existing:
        existing_rel = existing.get("relative_path")
        if isinstance(existing_rel, str):
            index = parse_existing_index(Path(existing_rel).name, stem)
    if index is None:
        index = next_index_ref[0]
        next_index_ref[0] += 1

    guessed = guess_extension_from_url(url)
    planned_ext = guessed if guessed in PASSTHROUGH_EXTENSIONS else ".webp"
    planned_relative = (Path(asset_dir.name) / f"{stem}_{index:03d}{planned_ext}").as_posix()

    if not config.apply:
        return ResolveResult(
            relative_path=planned_relative,
            status="planned",
        )

    filename, stored_format, source_content_type, digest = materialize_url(
        session=session,
        url=url,
        asset_dir=asset_dir,
        stem=stem,
        index=index,
        quality=config.quality,
        method=config.method,
    )
    relative = (Path(asset_dir.name) / filename).as_posix()
    now = utc_now_iso()
    created_at = now
    if existing and isinstance(existing.get("created_at_utc"), str):
        created_at = str(existing["created_at_utc"])

    metadata[url] = {
        "relative_path": relative,
        "content_sha256": digest,
        "source_content_type": source_content_type,
        "stored_format": stored_format,
        "created_at_utc": created_at,
        "last_verified_at_utc": now,
    }

    return ResolveResult(
        relative_path=relative,
        status="downloaded",
    )


def process_markdown_file(markdown_path: Path, config: Config, session) -> FileResult:
    """Process one markdown file from scan to optional write-back.

    Args:
        markdown_path: Markdown file path.
        config: Run configuration.
        session: Optional HTTP session used in apply mode.

    Returns:
        ``FileResult`` with counters, resolved URL map, and errors.
    """

    rel_markdown = to_posix_relative(markdown_path, config.root)
    result = FileResult(markdown_path=rel_markdown)

    content = markdown_path.read_text(encoding="utf-8")
    matches = list(iter_external_image_matches(content))
    result.image_links_found = len(matches)
    if not matches:
        return result

    asset_dir = markdown_path.parent / f"{markdown_path.stem}.assets"
    metadata_path = asset_dir / config.metadata_name
    metadata = load_metadata(metadata_path)
    metadata_before = json.dumps(metadata, ensure_ascii=False, sort_keys=True)

    next_index = [next_index_start(asset_dir=asset_dir, metadata=metadata, stem=markdown_path.stem)]
    url_to_relative: Dict[str, str] = {}

    for match in matches:
        url = match.url
        if url in url_to_relative:
            # Resolve once per URL; multiple markdown occurrences reuse mapping.
            continue
        try:
            resolved = resolve_url_for_markdown(
                config=config,
                session=session,
                markdown_path=markdown_path,
                url=url,
                metadata=metadata,
                asset_dir=asset_dir,
                stem=markdown_path.stem,
                next_index_ref=next_index,
            )
            url_to_relative[url] = resolved.relative_path
            if resolved.status == "reused":
                result.reused_urls += 1
            elif resolved.status == "planned":
                result.planned_urls += 1
            elif resolved.status == "downloaded":
                result.downloaded_urls += 1
        except Exception as exc:
            message = f"{rel_markdown}: {url}: {exc}"
            result.errors.append(message)
            # Strict mode halts at first unresolved URL for easier triage.
            if config.strict:
                raise

    result.resolved_urls = dict(url_to_relative)
    rewritten_content, rewritten_count = rewrite_markdown_with_mapping(content, url_to_relative)
    result.rewritten_links = rewritten_count
    result.would_change = rewritten_content != content

    if config.apply and result.would_change:
        markdown_path.write_text(rewritten_content, encoding="utf-8")
        result.wrote_markdown = True

    metadata_after = json.dumps(metadata, ensure_ascii=False, sort_keys=True)
    if config.apply and metadata_after != metadata_before:
        write_json(metadata_path, metadata)
        result.wrote_metadata = True

    return result


def summarize(results: Sequence[FileResult]) -> Dict[str, int]:
    """Aggregate global counters across file-level processing results.

    Args:
        results: Per-file processing results.

    Returns:
        Dictionary of top-level summary metrics used in console/report output.
    """

    return {
        "files_scanned": len(results),
        "files_with_image_links": sum(1 for r in results if r.image_links_found > 0),
        "total_image_links_found": sum(r.image_links_found for r in results),
        "rewritten_links": sum(r.rewritten_links for r in results),
        "reused_urls": sum(r.reused_urls for r in results),
        "planned_urls": sum(r.planned_urls for r in results),
        "downloaded_urls": sum(r.downloaded_urls for r in results),
        "files_would_change": sum(1 for r in results if r.would_change),
        "files_wrote_markdown": sum(1 for r in results if r.wrote_markdown),
        "files_wrote_metadata": sum(1 for r in results if r.wrote_metadata),
        "error_count": sum(len(r.errors) for r in results),
    }


def print_summary(config: Config, results: Sequence[FileResult]) -> None:
    """Print human-readable run summary to stdout/stderr.

    Args:
        config: Run configuration (used for mode labeling).
        results: Per-file processing results.
    """

    summary = summarize(results)
    mode = "APPLY" if config.apply else "DRY-RUN"
    print(f"[{mode}] processed {summary['files_scanned']} markdown files")
    print(
        "links: "
        f"found={summary['total_image_links_found']} "
        f"rewritten={summary['rewritten_links']} "
        f"reused_urls={summary['reused_urls']} "
        f"planned_urls={summary['planned_urls']} "
        f"downloaded_urls={summary['downloaded_urls']}"
    )
    print(
        "files: "
        f"would_change={summary['files_would_change']} "
        f"wrote_markdown={summary['files_wrote_markdown']} "
        f"wrote_metadata={summary['files_wrote_metadata']}"
    )
    if summary["error_count"] > 0:
        print(f"errors: {summary['error_count']}", file=sys.stderr)
        for file_result in results:
            for message in file_result.errors:
                print(f"  - {message}", file=sys.stderr)


def write_report(config: Config, results: Sequence[FileResult]) -> None:
    """Optionally write a machine-readable JSON report.

    Args:
        config: Run configuration, including optional ``report_json`` path.
        results: Per-file processing results.
    """

    if not config.report_json:
        return
    payload = {
        "generated_at_utc": utc_now_iso(),
        "mode": "apply" if config.apply else "dry-run",
        "root": str(config.root),
        "include": list(config.include),
        "exclude": list(config.exclude),
        "summary": summarize(results),
        "files": [dataclasses.asdict(item) for item in results],
    }
    write_json(config.report_json, payload)


def main() -> int:
    """Run CLI workflow end-to-end.

    Returns:
        Exit code: ``0`` on success, ``1`` when any processing error occurred,
        and ``2`` for argument or environment validation failures.
    """

    config = parse_args()
    if config.apply:
        ensure_apply_dependencies()

    if not config.root.is_dir():
        print(f"error: root does not exist: {config.root}", file=sys.stderr)
        return 2

    markdown_files = discover_markdown_files(config.root, config.include, config.exclude)
    if not markdown_files:
        print("No markdown files matched include/exclude rules.")
        return 0

    session = create_http_session() if config.apply else None
    results: List[FileResult] = []

    try:
        for markdown_path in markdown_files:
            try:
                file_result = process_markdown_file(markdown_path, config=config, session=session)
            except Exception as exc:
                # Fail-soft default: preserve per-file failures in result stream
                # instead of aborting the entire run.
                rel_markdown = to_posix_relative(markdown_path, config.root)
                file_result = FileResult(
                    markdown_path=rel_markdown,
                    errors=[f"{rel_markdown}: {exc}"],
                )
            results.append(file_result)
            if config.strict and file_result.errors:
                break
    finally:
        if session is not None:
            session.close()

    print_summary(config, results)
    write_report(config, results)
    summary = summarize(results)
    return 1 if summary["error_count"] > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
