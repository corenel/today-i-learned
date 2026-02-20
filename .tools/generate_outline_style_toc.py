#!/usr/bin/env python3
"""
generate_outline_style_toc.py — Generate a Markdown TOC with Outline-style heading slugs.

This script creates a table of contents for Markdown files using the same slug generation
rules as Outline's rich-markdown-editor (https://github.com/outline/outline).

Usage:
  python generate_outline_style_toc.py path/to/file.md [--min-level 1] [--max-level 6]

Features:
- Preserves CJK characters (Chinese, Japanese, Korean) in slugs
- Removes both ASCII and Unicode quotation marks
- Handles duplicate headings by appending numeric suffixes
- Supports both ATX (#) and Setext (underline) heading styles
- Ignores headings inside fenced code blocks

Slug generation process:
1. Replace Latin extended characters (ä→a, ñ→n, etc.)
2. Remove punctuation: ASCII [!"#$%&'()*+,/:;<=>?@[\\]^_`{|}~] and Unicode quotes ["" '' 「」 『』 《》]
3. Replace whitespace with hyphens
4. Preserve alphanumeric and Unicode word characters (including CJK)
5. Convert to lowercase
6. HTML-escape the result
7. Prefix with "h-" for DOM ID compatibility
8. Append "-N" for duplicate slugs (first occurrence has no suffix)

Example:
  Input heading:  ## ViTPose++: 回归简洁，以可扩展的视觉 Transformer 重定义通用姿态估计
  Output slug:    #h-vitpose-回归简洁-以可扩展的视觉-transformer-重定义通用姿态估计
"""

from __future__ import annotations

import re
import sys
import html
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import click
from loguru import logger

# -----------------------------
#  Slugification (Outline port)
# -----------------------------

# Characters to remove during slugification (matching Outline's behavior)
# Includes:
#   - ASCII punctuation: !"#$%&'()*+,/:;<=>?@[\]^_`{|}~
#   - Unicode curly quotes: "" (U+201C/U+201D) and '' (U+2018/U+2019)
#   - CJK corner brackets: 「」 (U+300C/U+300D) and 『』 (U+300E/U+300F)
#   - CJK angle brackets: 《》 (U+300A/U+300B)
REMOVE_RE = re.compile(
    r'[!"#$%&\'\.()*+,/:;<=>?@\[\]\\^_`{|}~\u201C\u201D\u2018\u2019\u300C\u300D\u300E\u300F\u300A\u300B]'
)

# Latin extended character mappings for ASCII normalization
# Maps accented/special characters to their ASCII equivalents (e.g., ä→a, ñ→n)
CHARMAP = {
    "ß": "ss",
    "à": "a",
    "á": "a",
    "â": "a",
    "ã": "a",
    "ä": "a",
    "å": "a",
    "æ": "ae",
    "ç": "c",
    "è": "e",
    "é": "e",
    "ê": "e",
    "ë": "e",
    "ì": "i",
    "í": "i",
    "î": "i",
    "ï": "i",
    "ð": "d",
    "ñ": "n",
    "ò": "o",
    "ó": "o",
    "ô": "o",
    "õ": "o",
    "ö": "o",
    "ő": "o",
    "ø": "o",
    "ù": "u",
    "ú": "u",
    "û": "u",
    "ü": "u",
    "ű": "u",
    "ý": "y",
    "þ": "th",
    "ÿ": "y",
    "ẞ": "SS",
    "À": "A",
    "Á": "A",
    "Â": "A",
    "Ã": "A",
    "Ä": "A",
    "Å": "A",
    "Æ": "AE",
    "Ç": "C",
    "È": "E",
    "É": "E",
    "Ê": "E",
    "Ë": "E",
    "Ì": "I",
    "Í": "I",
    "Î": "I",
    "Ï": "I",
    "Ð": "D",
    "Ñ": "N",
    "Ò": "O",
    "Ó": "O",
    "Ô": "O",
    "Õ": "O",
    "Ö": "O",
    "Ő": "O",
    "Ø": "O",
    "Ù": "U",
    "Ú": "U",
    "Û": "U",
    "Ü": "U",
    "Ű": "U",
    "Ý": "Y",
    "Þ": "TH",
    "Ÿ": "Y",
    "Œ": "OE",
    "œ": "oe",
    "Đ": "D",
    "đ": "d",
    "Ł": "L",
    "ł": "l",
}

_safe_slug_cache: dict[str, str] = {}


def _escape_for_dom_id(s: str) -> str:
    """
    HTML-escape special characters for safe use in DOM IDs.

    Escapes: & → &amp; < → &lt; > → &gt; " → &quot; ' → &#39;
    Equivalent to lodash's escape() function.
    """
    s = html.escape(s, quote=True)  # &, <, >, "
    s = s.replace("'", "&#39;")
    return s


def slugify_js_equiv(text: str) -> str:
    """
    Convert text to a URL-safe slug following JavaScript slugify library behavior.

    This implementation matches the behavior of the slugify npm package as used
    by Outline, with specific configuration to preserve Unicode characters
    (especially CJK) while removing punctuation.

    Args:
        text: The text to slugify

    Returns:
        A slugified string safe for URLs and DOM IDs

    Process:
        1. Replace Latin extended chars (ä→a, ñ→n)
        2. Remove punctuation defined in REMOVE_RE
        3. Replace whitespace with hyphens
        4. Keep only alphanumeric, hyphens, and non-space Unicode chars
        5. Clean up multiple/trailing hyphens
        6. Convert to lowercase
    """
    if text is None:
        text = ""

    # Step 1: Replace known Latin extended characters
    result = []
    for ch in text:
        result.append(CHARMAP.get(ch, ch))
    t = "".join(result)

    # Step 2: Remove specific punctuation (as per the regex)
    # This removes chars like / without replacement
    t = REMOVE_RE.sub("", t)

    # Step 3: Replace sequences of spaces/whitespace with single hyphen
    t = re.sub(r"\s+", "-", t)

    # Step 4: Clean up remaining non-word characters
    # Keep: letters, numbers, hyphens, and Unicode word characters (including CJK)
    new_parts = []
    for ch in t:
        if ch == "-" or ch.isalnum() or (ord(ch) > 127 and not ch.isspace()):
            # Keep: hyphen, alphanumeric (including CJK), and non-space Unicode
            new_parts.append(ch)
        elif ch.isspace():
            # Already handled in step 3
            continue
        else:
            # Replace other chars with hyphen only if not adjacent to another hyphen
            if new_parts and new_parts[-1] != "-":
                new_parts.append("-")

    t = "".join(new_parts)

    # Step 5: Clean up hyphens
    t = t.strip("-")
    t = re.sub(r"-{2,}", "-", t)  # collapse multiple hyphens

    # Step 6: Convert to lowercase
    t = t.lower()

    return t


def safe_slugify(text: str) -> str:
    """
    Generate a DOM-safe slug from text with 'h-' prefix.

    Combines slugification, HTML escaping, and prefixing to create
    slugs that are valid DOM IDs and won't conflict with numeric IDs.
    Results are cached for performance.

    Args:
        text: The heading text to convert

    Returns:
        A slug prefixed with 'h-' suitable for use as a DOM ID

    Example:
        >>> safe_slugify("Hello World!")
        "h-hello-world"
        >>> safe_slugify("测试 Test")
        "h-测试-test"
    """
    if text in _safe_slug_cache:
        return _safe_slug_cache[text]

    slug_core = slugify_js_equiv(text)
    escaped = _escape_for_dom_id(slug_core)
    result = f"h-{escaped}"
    _safe_slug_cache[text] = result
    return result


def heading_to_slug(text: str, index: int = 0) -> str:
    """
    Generate a unique slug for a heading with deduplication support.

    Args:
        text: The heading text
        index: Deduplication index (0 for first occurrence)

    Returns:
        A unique slug, with "-N" suffix for duplicates (N > 0)

    Example:
        >>> heading_to_slug("Introduction", 0)
        "h-introduction"
        >>> heading_to_slug("Introduction", 1)
        "h-introduction-1"
        >>> heading_to_slug("Introduction", 2)
        "h-introduction-2"
    """
    base = safe_slugify(text)
    if index == 0:
        return base
    return f"{base}-{index}"


def heading_to_persistence_key(
    text: str, id_: str | None = None, pathname: str | None = None
) -> str:
    """
    Generate a persistence key for storing heading collapsed state.

    Used by Outline's editor to remember which headings are collapsed.
    Format: "rme-{id or pathname}–{slug}" (note: uses en dash U+2013)

    Args:
        text: The heading text
        id_: Optional document ID
        pathname: Optional URL pathname (fallback if no ID)

    Returns:
        A persistence key string
    """
    slug = heading_to_slug(text, 0)
    path = id_ if id_ else (pathname or "")
    return f"rme-{path}–{slug}"  # en dash


# -----------------------------
#  Markdown heading extraction
# -----------------------------

ATX = re.compile(r"^(#{1,6})[ \t]+(.+?)\s*#*\s*$")
SETEXT_H1 = re.compile(r"^=+\s*$")
SETEXT_H2 = re.compile(r"^-+\s*$")
FENCE = re.compile(r"^(```|~~~)")


@dataclass
class Heading:
    level: int  # 1..6
    text: str  # raw heading text (approximate textContent)
    line: int  # line number (1-based)
    slug: str  # final unique slug (with h- prefix and any -N suffix)


def iter_headings(md_lines: Iterable[str]) -> Iterable[tuple[int, str, int]]:
    """
    Extract headings from Markdown lines.

    Yields:
        Tuples of (level, text, line_no) where:
        - level: 1-6 for heading depth
        - text: The heading text content
        - line_no: 1-based line number

    Features:
        - Supports ATX headings (# syntax)
        - Supports Setext headings (underline with = or -)
        - Ignores headings inside fenced code blocks
        - Handles optional closing # marks in ATX headings
    """
    in_fence = False
    prev_line: str | None = None
    prev_no: int = 0

    for i, raw in enumerate(md_lines, start=1):
        line = raw.rstrip("\n")

        # Toggle fenced code state
        if FENCE.match(line.strip()):
            in_fence = not in_fence
            prev_line = line
            prev_no = i
            continue

        if in_fence:
            prev_line = line
            prev_no = i
            continue

        # ATX
        m = ATX.match(line)
        if m:
            level = len(m.group(1))
            text = m.group(2).strip()
            yield (level, text, i)
            prev_line = line
            prev_no = i
            continue

        # Setext: look at underline style
        if prev_line and (SETEXT_H1.match(line) or SETEXT_H2.match(line)):
            text = prev_line.strip()
            if text and not ATX.match(
                text
            ):  # don't double-count if previous was ATX
                level = 1 if SETEXT_H1.match(line) else 2
                yield (level, text, prev_no)

        prev_line = line
        prev_no = i


def make_toc(headings_seq: Iterable[tuple[int, str, int]]) -> list[Heading]:
    """
    Build a table of contents with unique slugs for each heading.

    Implements Outline's deduplication strategy: first occurrence of a heading
    gets the base slug, subsequent duplicates get "-1", "-2", etc.

    Args:
        headings_seq: Iterable of (level, text, line_no) tuples

    Returns:
        List of Heading objects with unique slugs
    """
    counts: dict[str, int] = {}
    toc: list[Heading] = []

    for level, text, line_no in headings_seq:
        base = safe_slugify(text)
        idx = counts.get(base, 0)
        slug = heading_to_slug(text, idx)  # 0 => no suffix, 1 => -1, etc.
        counts[base] = idx + 1
        toc.append(Heading(level=level, text=text, line=line_no, slug=slug))

    return toc


def format_toc_markdown(
    toc: list[Heading], min_level: int = 1, max_level: int = 6
) -> str:
    """
    Format the table of contents as a Markdown bullet list.

    Args:
        toc: List of Heading objects
        min_level: Minimum heading level to include (1-6)
        max_level: Maximum heading level to include (1-6)

    Returns:
        Markdown-formatted TOC with indented bullet points and anchor links
    """
    lines = []
    for h in toc:
        if h.level < min_level or h.level > max_level:
            continue
        indent = "  " * (h.level - 1)
        # Link fragment is literally the slug string, including HTML entities if any
        lines.append(f"{indent}- [{h.text}](#{h.slug})")
    return "\n".join(lines)


# -----------------------------
#  CLI
# -----------------------------


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument(
    "markdown_file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
)
@click.option(
    "--min-level",
    type=click.IntRange(1, 6),
    default=1,
    show_default=True,
    help="Minimum heading depth to include.",
)
@click.option(
    "--max-level",
    type=click.IntRange(1, 6),
    default=6,
    show_default=True,
    help="Maximum heading depth to include.",
)
@click.option(
    "--verbose",
    "-v",
    count=True,
    help="Increase verbosity (can be used multiple times).",
)
def main(markdown_file: Path, min_level: int, max_level: int, verbose: int):
    """
    Generate a TOC for MARKDOWN_FILE using Outline-compatible heading slugs.
    """
    level_map = {0: "WARNING", 1: "INFO", 2: "DEBUG", 3: "TRACE"}
    logger.remove()
    logger.add(sys.stderr, level=level_map.get(verbose, "INFO"))

    logger.debug("Reading file: {}", markdown_file)
    text = markdown_file.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()

    logger.debug("Extracting headings…")
    heads = list(iter_headings(lines))
    if not heads:
        logger.warning("No headings found.")
        return

    logger.debug("Generating slugs and TOC…")
    toc = make_toc(heads)
    md_toc = format_toc_markdown(toc, min_level=min_level, max_level=max_level)

    click.echo(md_toc)


if __name__ == "__main__":
    main()
