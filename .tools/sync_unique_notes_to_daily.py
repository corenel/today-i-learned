#!/usr/bin/env python3
"""Synchronize timestamped Obsidian notes with their daily-note records.

The command scans a vault for Markdown files named ``YYYYMMDDHHMM_title.md`` and
checks whether each note's basename appears as a rendered wikilink in the daily
note encoded by the filename date. Missing links can be selected interactively or
approved in bulk. When a target daily note does not exist, the command creates it
from the configured template before inserting the links under ``## Daily Record``.

Daily-note settings are resolved in this order: explicit command-line arguments,
Obsidian's ``.obsidian/daily-notes.json``, then the legacy defaults in this module.
Path formats support ``YYYY``, ``MM``, and ``DD`` plus bracketed literals such as
``[Daily]``. Every configured and rendered path is resolved and required to remain
inside the vault.

The preview phase performs no writes. Selected changes are rendered from captured
file snapshots, revalidated immediately before staging and replacement, and written
through sibling temporary files. Links found only in a different date's daily note
are reported as mismatches; the command does not move or duplicate them.

Examples:
    Preview the current vault and choose links interactively::

        python .agents/tools/sync_unique_notes_to_daily.py --year 2026

    Apply every eligible link using explicit vault paths::

        python .agents/tools/sync_unique_notes_to_daily.py \\
            --vault /path/to/vault --daily-template Templates/Daily.md --yes
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import date, datetime
import importlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from typing import TextIO
import unicodedata


# Legacy daily-note root used when neither CLI nor Obsidian settings provide one.
DEFAULT_DAILY_ROOT = "0. PeriodicNotes"
# Legacy template path, interpreted relative to the vault by default.
DEFAULT_DAILY_TEMPLATE = "0. PeriodicNotes/Templates/Daily.md"
# Legacy path format; bracketed text is literal rather than a date token.
DEFAULT_DAILY_FORMAT = "YYYY/[Daily]/MM/YYYY-MM-DD"
# Obsidian core Daily Notes plugin settings, relative to the vault root.
OBSIDIAN_DAILY_CONFIG = Path(".obsidian/daily-notes.json")
# A unique note begins with a sortable, minute-resolution timestamp and underscore.
UNIQUE_NOTE_RE = re.compile(r"^(?P<timestamp>\d{12})_(?P<title>.+)$")
# Capture the target payload from normal or embedded Obsidian wikilinks.
WIKILINK_RE = re.compile(r"!?\[\[([^\[\]\r\n]+)\]\]")
# Match only a visible level-two Daily Record section heading.
DAILY_RECORD_HEADING_RE = re.compile(
    r"(?m)^[ \t]{0,3}##[ \t]+Daily[ \t]+Record(?:[ \t]+#*)?[ \t]*\r?$"
)
# A following level-one or level-two heading terminates the Daily Record section.
NEXT_SECTION_RE = re.compile(r"(?m)^[ \t]{0,3}#{1,2}(?:[ \t]+|$)")
# Recognize CommonMark-style backtick and tilde fences with optional indentation.
FENCE_RE = re.compile(r"^[ \t]{0,3}(`{3,}|~{3,})")


class SyncError(Exception):
    """Report a user-facing condition that prevents safe synchronization.

    The command catches this exception at its outer boundary, prints the message,
    and exits without intentionally applying further changes.
    """


class SelectionError(ValueError):
    """Report selection syntax or IDs that do not match the preview."""


@dataclass(frozen=True, slots=True)
class _FormatPart:
    """Represent one date token or literal segment in a path format.

    Attributes:
        kind: Either ``"token"`` or ``"literal"``.
        value: A supported date token or literal text copied into the path.
    """

    kind: str
    value: str


@dataclass(frozen=True, slots=True)
class DailyPathFormat:
    """Represent a validated, bidirectional daily-note path format.

    Attributes:
        source: Canonical format text without a trailing ``.md`` extension.
        parts: Ordered tokens and literals used to render paths.
        pattern: Full-path regular expression used to recover a date from a path.
    """

    source: str
    parts: tuple[_FormatPart, ...]
    pattern: re.Pattern[str]

    def relative_path(self, note_date: date) -> Path:
        """Render a Markdown path relative to the daily-note root.

        Args:
            note_date: Calendar date to substitute for each format token.

        Returns:
            The rendered relative path with a ``.md`` suffix.
        """

        values = {
            "YYYY": f"{note_date:%Y}",
            "MM": f"{note_date:%m}",
            "DD": f"{note_date:%d}",
        }
        rendered = "".join(
            values[part.value] if part.kind == "token" else part.value
            for part in self.parts
        )
        return Path(f"{rendered}.md")

    def parse_path(self, relative_path: Path) -> date | None:
        """Parse the calendar date encoded by a relative daily-note path.

        Args:
            relative_path: Markdown path relative to the configured daily root.

        Returns:
            The encoded date, or ``None`` when the path shape or date is invalid.
        """

        match = self.pattern.fullmatch(relative_path.as_posix())
        if match is None:
            return None
        try:
            return date(
                int(match.group("year")),
                int(match.group("month")),
                int(match.group("day")),
            )
        except ValueError:
            return None


@dataclass(frozen=True, slots=True)
class DailyNoteConfig:
    """Hold resolved, vault-contained settings for daily-note operations.

    Attributes:
        vault: Absolute, resolved vault root.
        root: Absolute daily-note directory contained by ``vault``.
        template: Absolute template path contained by ``vault``.
        path_format: Validated format for paths below ``root``.
    """

    vault: Path
    root: Path
    template: Path
    path_format: DailyPathFormat

    def target_path(self, note_date: date) -> Path:
        """Return the contained daily-note path for a date.

        Args:
            note_date: Date whose configured path should be rendered.

        Returns:
            Absolute, resolved path below both the vault and daily-note root.

        Raises:
            SyncError: If rendering or symlink resolution escapes an allowed root.
        """

        target = (
            self.root / self.path_format.relative_path(note_date)
        ).resolve()
        _require_within(self.vault, target, "rendered daily-note path")
        _require_within(self.root, target, "rendered daily-note path")
        return target


@dataclass(frozen=True, slots=True)
class UniqueNote:
    """Describe one unambiguous timestamp-prefixed Markdown note.

    Attributes:
        path: Absolute path to the source note.
        relative_path: Source path relative to the vault, used in diagnostics.
        basename: Filename without ``.md``; also the emitted wikilink target.
        timestamp: Valid timestamp decoded from the basename.
    """

    path: Path
    relative_path: Path
    basename: str
    timestamp: datetime

    @property
    def note_date(self) -> date:
        """Return the calendar date encoded in the filename timestamp."""

        return self.timestamp.date()

    @property
    def key(self) -> str:
        """Return the case-insensitive, Unicode-normalized wikilink key."""

        return normalize_note_key(self.basename)


@dataclass(frozen=True, slots=True)
class FileSnapshot:
    """Capture file state used for rendering and guarded writes.

    Attributes:
        path: Absolute, resolved path observed during the preview.
        data: Exact bytes used for later change detection.
        text: UTF-8 decoding of ``data`` used for Markdown processing.
        mode: Permission bits to preserve on a replacement or derived file.
    """

    path: Path
    data: bytes
    text: str
    mode: int


@dataclass(frozen=True, slots=True)
class DailyNote:
    """Describe a configured daily note and its rendered wikilinks.

    Attributes:
        note_date: Date decoded from the note's configured relative path.
        snapshot: File content and mode captured during discovery.
        link_keys: Normalized basenames linked from rendered Markdown content.
    """

    note_date: date
    snapshot: FileSnapshot
    link_keys: frozenset[str]


@dataclass(frozen=True, slots=True)
class Mismatch:
    """Describe a note linked only from daily notes with other dates.

    Attributes:
        note: Unique note whose filename date has no matching daily-note link.
        daily_notes: Other-date daily notes that already link to ``note``.
    """

    note: UniqueNote
    daily_notes: tuple[DailyNote, ...]


@dataclass(frozen=True, slots=True)
class Proposal:
    """Describe one missing note-to-daily-note link.

    Attributes:
        note: Unique note that has no rendered daily-note wikilink.
        target_path: Configured daily-note path for the note's filename date.
    """

    note: UniqueNote
    target_path: Path


@dataclass(frozen=True, slots=True)
class TargetSnapshot:
    """Hold the content source used to plan edits for one target date.

    Attributes:
        path: Absolute daily-note path to create or update.
        original: Existing target snapshot, or ``None`` for a new daily note.
        base_text: Existing daily-note text or template text to modify.
        mode: Permission bits inherited from the target or template.
    """

    path: Path
    original: FileSnapshot | None
    base_text: str
    mode: int


@dataclass(frozen=True, slots=True)
class NumberedProposal:
    """Pair a proposal with its stable, globally unique preview ID.

    Attributes:
        item_id: Positive integer accepted by every selection backend.
        proposal: Missing link represented by this selectable item.
    """

    item_id: int
    proposal: Proposal


@dataclass(frozen=True, slots=True)
class ProposalGroup:
    """Group selectable proposals that share one target daily note.

    Attributes:
        group_id: Stable display token such as ``D1``.
        note_date: Date shared by all proposals in the group.
        target: Snapshot and destination used to render a selected update.
        items: Timestamp-ordered, globally numbered proposals.
    """

    group_id: str
    note_date: date
    target: TargetSnapshot
    items: tuple[NumberedProposal, ...]


@dataclass(frozen=True, slots=True)
class SelectionRow:
    """Represent one group or item row for visual selector backends.

    Attributes:
        token: Machine-readable selection token returned by the backend.
        label: Human-readable preview text displayed for the token.
    """

    token: str
    label: str


@dataclass(frozen=True, slots=True)
class Classification:
    """Partition valid candidates by their daily-note link state.

    Attributes:
        satisfied: Notes linked from the daily note matching their filename date.
        mismatches: Notes linked only from one or more other dates.
        proposals: Notes with no rendered link in any configured daily note.
    """

    satisfied: tuple[UniqueNote, ...]
    mismatches: tuple[Mismatch, ...]
    proposals: tuple[Proposal, ...]


@dataclass(frozen=True, slots=True)
class PlannedWrite:
    """Describe a rendered daily-note update awaiting validation.

    Attributes:
        path: Absolute target path to create or replace.
        original: Preview snapshot, or ``None`` if the target did not exist.
        data: Complete UTF-8 file content to write.
        mode: Permission bits for the staged replacement file.
    """

    path: Path
    original: FileSnapshot | None
    data: bytes
    mode: int


@dataclass(slots=True)
class _MaskState:
    """Track multiline Markdown constructs while preserving source offsets.

    Attributes:
        fence_char: Active fenced-code marker character, or ``None``.
        fence_length: Minimum marker run that closes the active fence.
        html_comment: Whether scanning is inside an HTML comment.
        obsidian_comment: Whether scanning is inside an Obsidian ``%%`` comment.
        code_ticks: Backtick-run length that closes active inline code.
    """

    fence_char: str | None = None
    fence_length: int = 0
    html_comment: bool = False
    obsidian_comment: bool = False
    code_ticks: int = 0


def normalize_note_key(basename: str) -> str:
    """Normalize a basename for case-insensitive wikilink comparison.

    Args:
        basename: Note basename without a path requirement.

    Returns:
        NFC-normalized, case-folded text suitable for dictionary and set keys.
    """

    return unicodedata.normalize("NFC", basename).casefold()


def _require_within(container: Path, candidate: Path, label: str) -> None:
    """Require a resolved candidate path to remain below a container.

    Args:
        container: Absolute root that must contain ``candidate``.
        candidate: Absolute path to validate.
        label: Human-readable path role included in an error message.

    Raises:
        SyncError: If ``candidate`` is not equal to or below ``container``.
    """

    try:
        candidate.relative_to(container)
    except ValueError as error:
        raise SyncError(
            f"{label} escapes its allowed root: {candidate}"
        ) from error


def _resolve_vault_path(vault: Path, value: str | Path, label: str) -> Path:
    """Resolve a configured path and require it to remain inside the vault.

    Relative values are interpreted from the vault root. Expanding and resolving
    before the containment check also prevents existing symlinks from bypassing
    the boundary.

    Args:
        vault: Absolute, resolved vault directory.
        value: Absolute path or vault-relative configured value.
        label: Human-readable path role included in an error message.

    Returns:
        Absolute, resolved path contained by ``vault``.

    Raises:
        SyncError: If the resolved path escapes ``vault``.
    """

    raw = Path(value).expanduser()
    resolved = (raw if raw.is_absolute() else vault / raw).resolve()
    _require_within(vault, resolved, label)
    return resolved


def compile_daily_format(value: str) -> DailyPathFormat:
    """Compile supported Obsidian date tokens into a bidirectional path format.

    ``YYYY``, ``MM``, and ``DD`` must each appear at least once. Text inside square
    brackets is treated literally, as in Obsidian date formats. Repeated date
    tokens are accepted only when every occurrence has the same value during path
    parsing.

    Args:
        value: Obsidian-style path format, optionally ending in ``.md``.

    Returns:
        Validated parts for rendering and a regular expression for parsing.

    Raises:
        SyncError: If the format is empty, unsafe, ambiguous, incomplete, or uses
            unsupported date tokens.
    """

    source = value.strip()
    if source.lower().endswith(".md"):
        source = source[:-3]
    if not source:
        raise SyncError("daily-note format must not be empty")
    if "\\" in source or "\x00" in source:
        raise SyncError("daily-note format must use safe forward-slash paths")

    parts: list[_FormatPart] = []
    literal: list[str] = []
    seen_tokens: set[str] = set()

    def flush_literal() -> None:
        """Move the pending literal run into the compiled part sequence."""

        if literal:
            parts.append(_FormatPart("literal", "".join(literal)))
            literal.clear()

    index = 0
    while index < len(source):
        # Obsidian uses brackets to quote literal text that might resemble tokens.
        if source[index] == "[":
            closing = source.find("]", index + 1)
            if closing < 0:
                raise SyncError("daily-note format contains an unmatched '['")
            literal.append(source[index + 1 : closing])
            index = closing + 1
            continue
        if source[index] == "]":
            raise SyncError("daily-note format contains an unmatched ']'")

        token = next(
            (
                candidate
                for candidate in ("YYYY", "MM", "DD")
                if source.startswith(candidate, index)
            ),
            None,
        )
        if token is not None:
            flush_literal()
            parts.append(_FormatPart("token", token))
            seen_tokens.add(token)
            index += len(token)
            continue
        if source[index] in "YMD":
            run = re.match(r"[A-Za-z]+", source[index:])
            unsupported = run.group(0) if run is not None else source[index]
            raise SyncError(
                f"unsupported daily-note date token: {unsupported!r}"
            )

        literal.append(source[index])
        index += 1

    flush_literal()
    missing = {"YYYY", "MM", "DD"} - seen_tokens
    if missing:
        shown = ", ".join(sorted(missing))
        raise SyncError(
            f"daily-note format is missing required tokens: {shown}"
        )

    sample_values = {"YYYY": "2000", "MM": "12", "DD": "31"}
    sample = "".join(
        sample_values[part.value] if part.kind == "token" else part.value
        for part in parts
    )
    sample_path = Path(sample)
    # Validate the rendered shape once; substitution never introduces separators.
    if (
        sample_path.is_absolute()
        or ".." in sample_path.parts
        or sample in {"", "."}
        or sample.endswith("/")
        or sample_path.as_posix() != sample
    ):
        raise SyncError(
            "daily-note format must render a canonical relative path"
        )

    group_names = {"YYYY": "year", "MM": "month", "DD": "day"}
    group_patterns = {
        "YYYY": r"[0-9]{4}",
        "MM": r"[0-9]{2}",
        "DD": r"[0-9]{2}",
    }
    emitted: set[str] = set()
    regex_parts: list[str] = []
    for part in parts:
        if part.kind == "literal":
            regex_parts.append(re.escape(part.value))
            continue
        group_name = group_names[part.value]
        if group_name in emitted:
            # A backreference ensures repeated tokens encode the same date component.
            regex_parts.append(rf"(?P={group_name})")
        else:
            regex_parts.append(
                rf"(?P<{group_name}>{group_patterns[part.value]})"
            )
            emitted.add(group_name)

    pattern = re.compile("".join(regex_parts) + r"\.md")
    return DailyPathFormat(source=source, parts=tuple(parts), pattern=pattern)


def _load_obsidian_daily_settings(vault: Path) -> dict[str, str]:
    """Load supported values from Obsidian's core Daily Notes settings.

    Unknown JSON properties are ignored so the reader remains compatible with
    Obsidian configuration additions.

    Args:
        vault: Absolute vault root containing ``.obsidian``.

    Returns:
        Present, nonempty string values for ``folder``, ``template``, and
        ``format``. Returns an empty mapping when the settings file is absent.

    Raises:
        SyncError: If the file cannot be read as a JSON object or a supported
            property has an invalid value.
    """

    path = vault / OBSIDIAN_DAILY_CONFIG
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise SyncError(
            f"cannot read Obsidian daily-note settings {path}: {error}"
        ) from error
    if not isinstance(value, dict):
        raise SyncError(
            f"Obsidian daily-note settings must be a JSON object: {path}"
        )

    settings: dict[str, str] = {}
    for key in ("folder", "template", "format"):
        if key not in value:
            continue
        item = value[key]
        if not isinstance(item, str) or not item.strip():
            raise SyncError(
                f"Obsidian daily-note setting {key!r} must be a nonempty string"
            )
        settings[key] = item
    return settings


def resolve_daily_note_config(
    vault: Path,
    *,
    daily_notes_root: str | Path | None = None,
    daily_template: str | Path | None = None,
    daily_notes_format: str | None = None,
) -> DailyNoteConfig:
    """Resolve all settings into one safe daily-note configuration.

    Each explicit argument overrides its corresponding Obsidian Daily Notes
    setting, which in turn overrides the module's legacy default. Paths may be
    absolute or vault-relative but must resolve inside the vault.

    Args:
        vault: Vault root; it is resolved before other paths.
        daily_notes_root: Optional daily-note directory override.
        daily_template: Optional daily-note template override.
        daily_notes_format: Optional Obsidian-style path-format override.

    Returns:
        Resolved paths and a validated daily-note path format.

    Raises:
        SyncError: If settings are unreadable or any configured path or format is
            unsafe or invalid.
    """

    vault = vault.resolve()
    settings = _load_obsidian_daily_settings(vault)
    # Resolve each option independently so partial CLI overrides remain useful.
    root_value = (
        daily_notes_root
        if daily_notes_root is not None
        else settings.get("folder", DEFAULT_DAILY_ROOT)
    )
    template_value = (
        daily_template
        if daily_template is not None
        else settings.get("template", DEFAULT_DAILY_TEMPLATE)
    )
    format_value = (
        daily_notes_format
        if daily_notes_format is not None
        else settings.get("format", DEFAULT_DAILY_FORMAT)
    )

    root = _resolve_vault_path(vault, root_value, "daily-note root")
    template = _resolve_vault_path(
        vault, template_value, "daily-note template"
    )
    if root.exists() and not root.is_dir():
        raise SyncError(f"daily-note root is not a directory: {root}")
    if template.exists() and not template.is_file():
        raise SyncError(f"daily-note template is not a file: {template}")

    path_format = compile_daily_format(format_value)
    config = DailyNoteConfig(vault, root, template, path_format)
    # Exercise the complete rendering and containment contract before scanning.
    config.target_path(date(2000, 12, 31))
    return config


def target_daily_path(config: DailyNoteConfig, note_date: date) -> Path:
    """Return the configured vault path for a calendar date.

    Args:
        config: Resolved daily-note configuration.
        note_date: Date whose daily-note path should be rendered.

    Returns:
        Absolute path contained by the configured vault and daily-note root.

    Raises:
        SyncError: If the rendered path escapes a configured boundary.
    """

    return config.target_path(note_date)


def _iter_visible_markdown(vault: Path) -> Iterable[Path]:
    """Yield visible Markdown files in deterministic vault-relative order.

    Dot-directories such as ``.obsidian`` and ``.git`` are pruned before descent.
    Dot-prefixed files outside those directories are not otherwise excluded.

    Args:
        vault: Directory tree to traverse.

    Yields:
        Absolute Markdown paths sorted by their POSIX-style relative paths.
    """

    paths: list[Path] = []
    for root, directories, files in os.walk(vault):
        directories[:] = sorted(
            name for name in directories if not name.startswith(".")
        )
        root_path = Path(root)
        paths.extend(
            root_path / name for name in files if name.lower().endswith(".md")
        )
    yield from sorted(
        paths, key=lambda path: path.relative_to(vault).as_posix()
    )


def discover_unique_notes(
    vault: Path,
    start: date | None = None,
    end: date | None = None,
) -> tuple[tuple[UniqueNote, ...], tuple[str, ...]]:
    """Discover unambiguous unique notes within inclusive date bounds.

    Files must have a basename shaped as ``YYYYMMDDHHMM_title`` with a valid
    minute-resolution timestamp. Basenames that compare equal after NFC
    normalization and case folding are all skipped because a basename-only
    wikilink cannot identify one copy safely.

    Args:
        vault: Absolute vault root to scan recursively.
        start: Optional inclusive lower filename-date bound.
        end: Optional inclusive upper filename-date bound.

    Returns:
        A pair containing timestamp-ordered candidates and non-fatal warnings for
        invalid timestamps or ambiguous basenames.
    """

    candidates: list[UniqueNote] = []
    warnings: list[str] = []

    for path in _iter_visible_markdown(vault):
        match = UNIQUE_NOTE_RE.fullmatch(path.stem)
        if match is None:
            continue
        try:
            timestamp = datetime.strptime(
                match.group("timestamp"), "%Y%m%d%H%M"
            )
        except ValueError:
            warnings.append(
                f"Invalid timestamp; skipped {path.relative_to(vault).as_posix()}"
            )
            continue
        if start is not None and timestamp.date() < start:
            continue
        if end is not None and timestamp.date() > end:
            continue
        candidates.append(
            UniqueNote(
                path=path,
                relative_path=path.relative_to(vault),
                basename=path.stem,
                timestamp=timestamp,
            )
        )

    # Obsidian basename links are ambiguous when normalized names collide anywhere.
    by_key: dict[str, list[UniqueNote]] = defaultdict(list)
    for candidate in candidates:
        by_key[candidate.key].append(candidate)

    ambiguous_keys = {key for key, notes in by_key.items() if len(notes) > 1}
    for key in sorted(ambiguous_keys):
        paths = ", ".join(
            note.relative_path.as_posix()
            for note in sorted(
                by_key[key], key=lambda item: item.relative_path.as_posix()
            )
        )
        warnings.append(f"Ambiguous basename; skipped all copies: {paths}")

    valid = [
        candidate
        for candidate in candidates
        if candidate.key not in ambiguous_keys
    ]
    valid.sort(
        key=lambda note: (note.timestamp, note.relative_path.as_posix())
    )
    return tuple(valid), tuple(warnings)


def _mask_characters(value: str) -> str:
    """Replace visible characters with spaces while preserving line endings.

    Args:
        value: Source fragment to hide from later regular-expression searches.

    Returns:
        A fragment of identical length whose ``\n`` and ``\r`` positions match
        ``value``.
    """

    return "".join(
        "\n" if char == "\n" else "\r" if char == "\r" else " "
        for char in value
    )


def _mask_inline_constructs(line: str, state: _MaskState) -> str:
    """Mask comments and inline code while preserving source offsets.

    The mutable state allows HTML comments, Obsidian comments, and inline code to
    continue across physical lines. Markdown outside those constructs is copied
    unchanged for later heading and wikilink searches.

    Args:
        line: One source line, including its line ending when present.
        state: Scanner state inherited from preceding lines and updated in place.

    Returns:
        Text with non-rendered constructs replaced by equal-width whitespace.
    """

    output: list[str] = []
    index = 0
    while index < len(line):
        # Active constructs take precedence over opener detection in their content.
        if state.html_comment:
            closing = line.find("-->", index)
            if closing < 0:
                output.append(_mask_characters(line[index:]))
                break
            output.append(_mask_characters(line[index : closing + 3]))
            index = closing + 3
            state.html_comment = False
            continue

        if state.obsidian_comment:
            closing = line.find("%%", index)
            if closing < 0:
                output.append(_mask_characters(line[index:]))
                break
            output.append(_mask_characters(line[index : closing + 2]))
            index = closing + 2
            state.obsidian_comment = False
            continue

        if state.code_ticks:
            run = 0
            while index + run < len(line) and line[index + run] == "`":
                run += 1
            if run == state.code_ticks:
                output.append(" " * run)
                index += run
                state.code_ticks = 0
            elif run:
                output.append(" " * run)
                index += run
            else:
                output.append(_mask_characters(line[index]))
                index += 1
            continue

        if line.startswith("<!--", index):
            output.append(" " * 4)
            index += 4
            state.html_comment = True
            continue
        if line.startswith("%%", index):
            output.append(" " * 2)
            index += 2
            state.obsidian_comment = True
            continue
        if line[index] == "`":
            run = 1
            while index + run < len(line) and line[index + run] == "`":
                run += 1
            output.append(" " * run)
            index += run
            state.code_ticks = run
            continue

        output.append(line[index])
        index += 1

    return "".join(output)


def mask_nonrendered_markdown(text: str) -> str:
    """Mask Markdown constructs that do not render as headings or wikilinks.

    Fenced code, inline code, HTML comments, and Obsidian ``%%`` comments are
    replaced with whitespace. The result has the same length and line-ending
    offsets as the input, so match spans can still index the original text.

    Args:
        text: Complete Markdown document.

    Returns:
        Offset-preserving text containing only potentially rendered Markdown.
    """

    state = _MaskState()
    output: list[str] = []

    for line in text.splitlines(keepends=True):
        if state.fence_char is not None:
            # Fence content is entirely non-rendered, including the closing marker.
            output.append(_mask_characters(line))
            stripped = line.lstrip(" \t")
            run = len(stripped) - len(stripped.lstrip(state.fence_char))
            if run >= state.fence_length:
                state.fence_char = None
                state.fence_length = 0
            continue

        # A fence marker inside a comment or inline-code span is ordinary content.
        if not (
            state.html_comment or state.obsidian_comment or state.code_ticks
        ):
            fence = FENCE_RE.match(line)
            if fence is not None:
                marker = fence.group(1)
                state.fence_char = marker[0]
                state.fence_length = len(marker)
                output.append(_mask_characters(line))
                continue

        output.append(_mask_inline_constructs(line, state))

    return "".join(output)


def extract_wikilink_keys(text: str) -> frozenset[str]:
    """Extract normalized note basenames from rendered Obsidian wikilinks.

    Embeds, aliases, heading fragments, directory components, and an optional
    ``.md`` suffix do not affect matching. Links inside code or comments are
    ignored.

    Args:
        text: Complete daily-note Markdown.

    Returns:
        Distinct, case-insensitive basename keys referenced by visible wikilinks.
    """

    visible = mask_nonrendered_markdown(text)
    keys: set[str] = set()
    for match in WIKILINK_RE.finditer(visible):
        # Obsidian resolves the target before aliases and heading/block fragments.
        target = match.group(1).split("|", 1)[0].split("#", 1)[0].strip()
        if not target:
            continue
        target = target.replace("\\", "/").rsplit("/", 1)[-1]
        if target.lower().endswith(".md"):
            target = target[:-3]
        if target:
            keys.add(normalize_note_key(target))
    return frozenset(keys)


def read_snapshot(path: Path) -> FileSnapshot:
    """Read a UTF-8 file and capture state needed by guarded writes.

    Args:
        path: Existing Markdown file to snapshot.

    Returns:
        Exact bytes, decoded text, and permission bits observed for ``path``.

    Raises:
        SyncError: If the file cannot be read, decoded as UTF-8, or inspected.
    """

    try:
        data = path.read_bytes()
        text = data.decode("utf-8")
        mode = stat.S_IMODE(path.stat().st_mode)
    except (OSError, UnicodeError) as error:
        raise SyncError(
            f"Cannot read UTF-8 Markdown file {path}: {error}"
        ) from error
    return FileSnapshot(path=path, data=data, text=text, mode=mode)


def discover_daily_notes(config: DailyNoteConfig) -> tuple[DailyNote, ...]:
    """Discover and parse daily notes matching the configured path format.

    Markdown files below the daily root that do not match the exact format are
    ignored. A missing daily root is treated as an empty collection because it may
    be created later for selected proposals.

    Args:
        config: Resolved daily-note paths and path format.

    Returns:
        Matching daily notes with snapshots and normalized rendered link keys.

    Raises:
        SyncError: If a matching daily note cannot be read as UTF-8.
    """

    root = config.root
    daily_notes: list[DailyNote] = []
    if not root.exists():
        return ()

    for path in _iter_visible_markdown(root):
        note_date = config.path_format.parse_path(path.relative_to(root))
        if note_date is None:
            continue
        snapshot = read_snapshot(path)
        daily_notes.append(
            DailyNote(
                note_date=note_date,
                snapshot=snapshot,
                link_keys=extract_wikilink_keys(snapshot.text),
            )
        )
    return tuple(daily_notes)


def classify_notes(
    config: DailyNoteConfig,
    candidates: Sequence[UniqueNote],
    daily_notes: Sequence[DailyNote],
) -> Classification:
    """Partition candidate notes by where their basename is linked.

    A same-date link always satisfies a candidate, even if other daily notes also
    link it. A candidate linked only on other dates becomes a report-only mismatch.
    Only candidates with no rendered daily-note link become insertion proposals.

    Args:
        config: Configuration used to render proposal target paths.
        candidates: Unambiguous unique notes to classify.
        daily_notes: Configured daily notes and their rendered link keys.

    Returns:
        Disjoint, order-preserving satisfied, mismatch, and proposal collections.

    Raises:
        SyncError: If a proposal's rendered target path escapes its allowed root.
    """

    links_by_key: dict[str, list[DailyNote]] = defaultdict(list)
    for daily_note in daily_notes:
        for key in daily_note.link_keys:
            links_by_key[key].append(daily_note)

    satisfied: list[UniqueNote] = []
    mismatches: list[Mismatch] = []
    proposals: list[Proposal] = []

    for candidate in candidates:
        linked_daily_notes = sorted(
            links_by_key.get(candidate.key, ()),
            key=lambda daily: (
                daily.note_date,
                daily.snapshot.path.as_posix(),
            ),
        )
        # Correct-date presence wins; cross-date links are noteworthy only in its absence.
        if any(
            daily.note_date == candidate.note_date
            for daily in linked_daily_notes
        ):
            satisfied.append(candidate)
        elif linked_daily_notes:
            mismatches.append(Mismatch(candidate, tuple(linked_daily_notes)))
        else:
            proposals.append(
                Proposal(
                    note=candidate,
                    target_path=target_daily_path(config, candidate.note_date),
                )
            )

    return Classification(
        tuple(satisfied), tuple(mismatches), tuple(proposals)
    )


def _daily_record_heading(text: str) -> re.Match[str]:
    """Locate the sole visible ``## Daily Record`` heading.

    Args:
        text: Complete daily-note or template Markdown.

    Returns:
        Match whose offsets index the original, unmasked text.

    Raises:
        SyncError: If no visible heading or more than one visible heading exists.
    """

    visible = mask_nonrendered_markdown(text)
    matches = list(DAILY_RECORD_HEADING_RE.finditer(visible))
    if len(matches) != 1:
        raise SyncError(
            f"expected exactly one visible '## Daily Record' heading, found {len(matches)}"
        )
    return matches[0]


def _newline_for(text: str) -> str:
    """Choose the dominant newline style for inserted text.

    Args:
        text: Existing file or template text.

    Returns:
        ``"\r\n"`` when CRLF occurrences outnumber lone LF occurrences;
        otherwise ``"\n"``.
    """

    return (
        "\r\n"
        if text.count("\r\n") > text.count("\n") - text.count("\r\n")
        else "\n"
    )


def render_daily_record(text: str, basenames: Sequence[str]) -> str:
    """Append wikilinks to a daily note's visible Daily Record section.

    Existing section content is preserved. New entries continue an existing list
    directly; otherwise a blank line separates them from prose. A following H1 or
    H2 section remains separated by one blank line, and the source newline style is
    retained.

    Args:
        text: Existing daily-note text or pristine template text.
        basenames: Note basenames to append in caller-provided order.

    Returns:
        Complete rendered document, or ``text`` unchanged when ``basenames`` is
        empty.

    Raises:
        SyncError: If ``text`` lacks exactly one visible Daily Record heading.
    """

    if not basenames:
        return text

    heading = _daily_record_heading(text)
    visible = mask_nonrendered_markdown(text)
    line_end = visible.find("\n", heading.end())
    line_end = len(text) if line_end < 0 else line_end + 1
    # H3 and deeper headings remain part of Daily Record; only peer/parent sections end it.
    next_heading = NEXT_SECTION_RE.search(visible, line_end)
    section_end = (
        next_heading.start() if next_heading is not None else len(text)
    )

    newline = _newline_for(text)
    # Rebuild only trailing section whitespace, leaving all substantive content byte-for-byte.
    trimmed_end = section_end
    while trimmed_end > line_end and text[trimmed_end - 1] in " \t\r\n":
        trimmed_end -= 1

    existing_section = text[line_end:trimmed_end]
    links = newline.join(f"- [[{basename}]]" for basename in basenames)

    if existing_section.strip():
        last_line = existing_section.splitlines()[-1]
        # Continue list-like content compactly; separate prose from generated bullets.
        separator = (
            newline
            if re.match(r"^[ \t]*(?:[-+*]|\d+[.)])[ \t]+", last_line)
            else newline * 2
        )
        prefix = text[:trimmed_end] + separator + links
    else:
        heading_line = text[:line_end].rstrip("\r\n")
        prefix = heading_line + newline * 2 + links

    if next_heading is not None:
        return prefix + newline * 2 + text[section_end:]
    return prefix + newline


def prepare_proposal_groups(
    config: DailyNoteConfig,
    proposals: Sequence[Proposal],
    daily_notes: Sequence[DailyNote],
) -> tuple[tuple[ProposalGroup, ...], tuple[str, ...], FileSnapshot | None]:
    """Validate proposal targets and assign stable selection IDs.

    Existing targets supply their own content and mode. Missing targets share one
    captured template snapshot. A malformed target is omitted with a warning so it
    cannot be selected or partially edited.

    Args:
        config: Resolved daily-note configuration.
        proposals: Unlinked notes and their intended target paths.
        daily_notes: Discovered daily notes used to identify existing targets.

    Returns:
        Date-ordered proposal groups, non-fatal target warnings, and the template
        snapshot when at least one proposed target is missing.

    Raises:
        SyncError: If a required template is absent or unreadable.
    """

    if not proposals:
        return (), (), None

    daily_by_path = {daily.snapshot.path: daily for daily in daily_notes}
    proposals_by_date: dict[date, list[Proposal]] = defaultdict(list)
    for proposal in proposals:
        proposals_by_date[proposal.note.note_date].append(proposal)

    # Capture the template once so every proposed creation uses identical preview state.
    template: FileSnapshot | None = None
    if any(
        target_daily_path(config, day) not in daily_by_path
        for day in proposals_by_date
    ):
        template_path = config.template
        if not template_path.is_file():
            raise SyncError(
                f"Daily-note template does not exist: {template_path}"
            )
        template = read_snapshot(template_path)

    warnings: list[str] = []
    groups: list[ProposalGroup] = []
    next_item_id = 1

    for day in sorted(proposals_by_date):
        path = target_daily_path(config, day)
        existing = daily_by_path.get(path)
        base_snapshot = existing.snapshot if existing is not None else template
        assert base_snapshot is not None
        try:
            _daily_record_heading(base_snapshot.text)
        except SyncError as error:
            relative = path.relative_to(config.vault).as_posix()
            warnings.append(f"Cannot update {relative}: {error}")
            continue

        # Stable numbering makes preview IDs deterministic across equivalent runs.
        sorted_proposals = sorted(
            proposals_by_date[day],
            key=lambda proposal: (
                proposal.note.timestamp,
                proposal.note.relative_path.as_posix(),
            ),
        )
        numbered: list[NumberedProposal] = []
        for proposal in sorted_proposals:
            numbered.append(NumberedProposal(next_item_id, proposal))
            next_item_id += 1

        groups.append(
            ProposalGroup(
                group_id=f"D{len(groups) + 1}",
                note_date=day,
                target=TargetSnapshot(
                    path=path,
                    original=existing.snapshot
                    if existing is not None
                    else None,
                    base_text=base_snapshot.text,
                    mode=base_snapshot.mode,
                ),
                items=tuple(numbered),
            )
        )

    return tuple(groups), tuple(warnings), template


def print_preview(
    vault: Path,
    candidates: Sequence[UniqueNote],
    classification: Classification,
    groups: Sequence[ProposalGroup],
    warnings: Sequence[str],
    output: TextIO,
) -> None:
    """Print the complete read-only preview and selectable changes.

    Args:
        vault: Vault root used to shorten paths in diagnostics.
        candidates: All valid unique notes included by the date filter.
        classification: Link-state partition used for summary counts and reports.
        groups: Eligible create/update groups and their selection IDs.
        warnings: Non-fatal discovery and target-validation warnings.
        output: Text stream that receives the preview.
    """

    selectable_count = sum(len(group.items) for group in groups)
    print(f"Scanned {len(candidates)} unique notes.", file=output)
    print(
        f"Already recorded on the filename date: {len(classification.satisfied)}",
        file=output,
    )
    print(
        f"Cross-date mismatches: {len(classification.mismatches)}", file=output
    )
    print(f"Selectable missing links: {selectable_count}", file=output)

    if warnings:
        print("\nWarnings:", file=output)
        for warning in warnings:
            print(f"  - {warning}", file=output)

    if classification.mismatches:
        print("\nCross-date mismatches (reported only):", file=output)
        for mismatch in classification.mismatches:
            locations = ", ".join(
                daily.snapshot.path.relative_to(vault).as_posix()
                for daily in mismatch.daily_notes
            )
            print(
                f"  - [[{mismatch.note.basename}]] targets {mismatch.note.note_date.isoformat()}; "
                f"linked from {locations}",
                file=output,
            )

    if groups:
        print("\nProposed changes:", file=output)
        for group in groups:
            action = (
                "update" if group.target.original is not None else "create"
            )
            relative = group.target.path.relative_to(vault).as_posix()
            print(
                f"  [{group.group_id}] {group.note_date.isoformat()} "
                f"({action} {relative})",
                file=output,
            )
            for numbered in group.items:
                note = numbered.proposal.note
                print(
                    f"    [{numbered.item_id}] [[{note.basename}]] "
                    f"<- {note.relative_path.as_posix()}",
                    file=output,
                )


def _expand_numeric_range(
    token: str, prefix: str, valid: set[int]
) -> set[int]:
    """Parse one selection ID or inclusive range.

    Args:
        token: Text such as ``"4"``, ``"4-6"``, ``"D2"``, or ``"D2-D4"``.
        prefix: Required case-insensitive prefix, or an empty string for item IDs.
        valid: Complete set of IDs displayed in the preview.

    Returns:
        Expanded set of validated integer IDs.

    Raises:
        SelectionError: If syntax is invalid, a range is reversed, or an ID was
            not displayed in the preview.
    """

    pattern = rf"{re.escape(prefix)}(\d+)(?:-{re.escape(prefix)}(\d+))?"
    match = re.fullmatch(pattern, token, flags=re.IGNORECASE)
    if match is None:
        raise SelectionError(f"invalid selection token: {token!r}")
    first = int(match.group(1))
    last = int(match.group(2)) if match.group(2) is not None else first
    if first > last:
        raise SelectionError(f"reversed selection range: {token!r}")
    selected = set(range(first, last + 1))
    missing = selected - valid
    if missing:
        shown = ", ".join(f"{prefix}{value}" for value in sorted(missing))
        raise SelectionError(f"unknown selection ID: {shown}")
    return selected


def parse_selection(
    value: str, groups: Sequence[ProposalGroup]
) -> frozenset[int]:
    """Resolve selection grammar to global proposal item IDs.

    Input is a comma-separated mixture of date-group IDs and item IDs. Group IDs
    expand to all items in those groups, overlapping terms are deduplicated, and
    ``all`` or ``none`` may be used alone.

    Args:
        value: User or selector input to parse.
        groups: Preview groups defining every valid group and item ID.

    Returns:
        Immutable set of selected global item IDs.

    Raises:
        SelectionError: If syntax, combinations, ranges, or referenced IDs are
            invalid.
    """

    group_items = {
        index: {item.item_id for item in group.items}
        for index, group in enumerate(groups, start=1)
    }
    valid_groups = set(group_items)
    valid_items = {
        item_id for items in group_items.values() for item_id in items
    }

    normalized = value.strip()
    if not normalized or normalized.casefold() == "none":
        return frozenset()
    if normalized.casefold() == "all":
        return frozenset(valid_items)

    # A set naturally deduplicates overlapping group, item, and range selections.
    selected: set[int] = set()
    tokens = [token.strip() for token in normalized.split(",")]
    if any(not token for token in tokens):
        raise SelectionError("selection contains an empty token")
    if any(token.casefold() in {"all", "none"} for token in tokens):
        raise SelectionError("'all' and 'none' must be used alone")

    for token in tokens:
        if token[:1].casefold() == "d":
            group_numbers = _expand_numeric_range(token, "D", valid_groups)
            for group_number in group_numbers:
                selected.update(group_items[group_number])
        else:
            selected.update(_expand_numeric_range(token, "", valid_items))

    return frozenset(selected)


def prompt_for_selection(
    groups: Sequence[ProposalGroup],
    input_stream: TextIO,
    output: TextIO,
) -> frozenset[int]:
    """Prompt until the user enters a valid batch selection.

    End-of-file is treated as selecting nothing, which makes cancellation safe in
    terminals and test streams.

    Args:
        groups: Preview groups that define valid selection IDs.
        input_stream: Stream from which one selection line is read per attempt.
        output: Stream receiving instructions, prompts, and validation errors.

    Returns:
        Selected global item IDs, or an empty set on EOF or an empty/``none`` entry.
    """

    print(
        "\nSelect all, none, date groups (D1,D3 or D1-D3), "
        "or link items (1,4-6). Mixed selections are allowed.",
        file=output,
    )
    while True:
        print("Selection [none]: ", end="", flush=True, file=output)
        value = input_stream.readline()
        if value == "":
            return frozenset()
        try:
            return parse_selection(value, groups)
        except SelectionError as error:
            print(f"Invalid selection: {error}", file=output)


def selection_rows(
    groups: Sequence[ProposalGroup],
) -> tuple[SelectionRow, ...]:
    """Build stable date-group and item rows for visual selectors.

    Args:
        groups: Numbered proposal groups in preview order.

    Returns:
        Alternating group and child-item rows with machine-readable tokens.
    """

    rows: list[SelectionRow] = []
    for group in groups:
        noun = "link" if len(group.items) == 1 else "links"
        rows.append(
            SelectionRow(
                group.group_id,
                f"[{group.group_id}] {group.note_date.isoformat()} "
                f"- all {len(group.items)} {noun}",
            )
        )
        for item in group.items:
            note = item.proposal.note
            rows.append(
                SelectionRow(
                    str(item.item_id),
                    f"  [{item.item_id}] [[{note.basename}]] "
                    f"<- {note.relative_path.as_posix()}",
                )
            )
    return tuple(rows)


def select_with_fzf(
    groups: Sequence[ProposalGroup], executable: str
) -> frozenset[int]:
    """Run ``fzf --multi`` and resolve selected group and item rows.

    Args:
        groups: Preview groups to present.
        executable: Resolved ``fzf`` executable path or command name.

    Returns:
        Selected global item IDs. Escape, interruption, or no rows yields an empty
        set and therefore no writes.

    Raises:
        SyncError: If ``fzf`` cannot start, exits unexpectedly, or returns tokens
            outside the displayed selection contract.
    """

    candidates = "".join(
        f"{row.token}\t{row.label}\n" for row in selection_rows(groups)
    )
    command = [
        executable,
        "--multi",
        "--height=80%",
        "--layout=reverse",
        "--border",
        "--delimiter=\t",
        "--with-nth=2..",
        "--prompt=Select> ",
        "--header=Space: toggle  Enter: confirm  Esc: none  Ctrl-A/Ctrl-D: all/none",
        "--bind=space:toggle,ctrl-a:select-all,ctrl-d:deselect-all",
    ]
    try:
        result = subprocess.run(
            command,
            input=candidates,
            text=True,
            stdout=subprocess.PIPE,
            check=False,
        )
    except OSError as error:
        raise SyncError(f"cannot start fzf selector: {error}") from error
    if result.returncode in {1, 130}:
        return frozenset()
    if result.returncode != 0:
        raise SyncError(f"fzf selector failed with status {result.returncode}")

    # Only the hidden first column is authoritative; labels are display text.
    tokens = [
        line.partition("\t")[0] for line in result.stdout.splitlines() if line
    ]
    if not tokens:
        return frozenset()
    try:
        return parse_selection(",".join(tokens), groups)
    except SelectionError as error:
        raise SyncError(
            f"fzf returned an invalid selection: {error}"
        ) from error


def questionary_available() -> bool:
    """Check whether the optional ``questionary`` selector can be imported.

    Returns:
        ``True`` when import machinery can resolve ``questionary``; otherwise
        ``False``. Broken import metadata is treated as unavailable.
    """

    try:
        return importlib.util.find_spec("questionary") is not None
    except (ImportError, ValueError):
        return False


def select_with_questionary(groups: Sequence[ProposalGroup]) -> frozenset[int]:
    """Run the optional ``questionary`` checkbox selector.

    Args:
        groups: Preview groups to present as group and item checkboxes.

    Returns:
        Selected global item IDs. Cancellation, interruption, or no checked rows
        yields an empty set and therefore no writes.

    Raises:
        SyncError: If the optional module is unavailable or returns invalid tokens.
    """

    try:
        questionary = importlib.import_module("questionary")
    except ImportError as error:
        raise SyncError(
            "questionary is not installed; run with "
            "'uv run --with questionary python ... --selector questionary'"
        ) from error

    choices = [
        questionary.Choice(title=row.label, value=row.token, checked=False)
        for row in selection_rows(groups)
    ]
    try:
        answer = questionary.checkbox(
            "Select links (Space toggles, Enter confirms):", choices=choices
        ).ask()
    except (EOFError, KeyboardInterrupt):
        return frozenset()
    if not answer:
        return frozenset()
    try:
        return parse_selection(",".join(answer), groups)
    except SelectionError as error:
        raise SyncError(
            f"questionary returned an invalid selection: {error}"
        ) from error


def choose_selection(
    groups: Sequence[ProposalGroup],
    selector: str,
    input_stream: TextIO,
    output: TextIO,
) -> frozenset[int]:
    """Select proposals through an explicit backend or automatic fallback chain.

    Explicit backend requests fail when their dependency is unavailable. ``auto``
    prefers ``fzf``, then ``questionary``, and finally the dependency-free text
    prompt.

    Args:
        groups: Preview groups eligible for selection.
        selector: One of ``auto``, ``fzf``, ``questionary``, or ``text``.
        input_stream: Input used by the text fallback.
        output: Stream receiving backend notices and text prompts.

    Returns:
        Selected global item IDs; an empty set represents cancellation.

    Raises:
        SyncError: If an explicit or selected visual backend cannot be used safely.
    """

    if selector == "text":
        return prompt_for_selection(groups, input_stream, output)

    fzf = shutil.which("fzf")
    if selector == "fzf":
        if fzf is None:
            raise SyncError(
                "fzf selector requested, but 'fzf' is not installed"
            )
        return select_with_fzf(groups, fzf)

    if selector == "questionary":
        if not questionary_available():
            raise SyncError(
                "questionary selector requested, but questionary is not installed; "
                "use 'uv run --with questionary python ... --selector questionary'"
            )
        return select_with_questionary(groups)

    # Automatic mode degrades gracefully without making optional packages mandatory.
    if fzf is not None:
        print("\nUsing fzf for interactive selection.", file=output)
        return select_with_fzf(groups, fzf)
    if questionary_available():
        print("\nUsing questionary for interactive selection.", file=output)
        return select_with_questionary(groups)

    script = Path(__file__).resolve()
    print(
        "\nNeither fzf nor questionary is available; using the text selector.\n"
        "For visual checkboxes, run:\n"
        f"  uv run --with questionary python {script} --selector questionary ...",
        file=output,
    )
    return prompt_for_selection(groups, input_stream, output)


def build_planned_writes(
    groups: Sequence[ProposalGroup], selected_ids: frozenset[int]
) -> tuple[PlannedWrite, ...]:
    """Render at most one complete file write per selected target date.

    Args:
        groups: Preview groups containing target snapshots and numbered proposals.
        selected_ids: Global item IDs approved by the user or ``--yes``.

    Returns:
        Date-group-ordered writes for groups with at least one selected item.

    Raises:
        SyncError: If a selected group's base text no longer satisfies the Daily
            Record rendering contract.
    """

    writes: list[PlannedWrite] = []
    for group in groups:
        selected = [
            item.proposal.note.basename
            for item in group.items
            if item.item_id in selected_ids
        ]
        if not selected:
            continue
        rendered = render_daily_record(group.target.base_text, selected)
        writes.append(
            PlannedWrite(
                path=group.target.path,
                original=group.target.original,
                data=rendered.encode("utf-8"),
                mode=group.target.mode,
            )
        )
    return tuple(writes)


def validate_snapshots(
    writes: Sequence[PlannedWrite], template: FileSnapshot | None
) -> None:
    """Require selected targets and their template to match preview snapshots.

    Resolved-path equality detects a changed symlink chain as well as ordinary
    content races. Existing files must retain their exact bytes, while targets
    planned for creation must still be absent.

    Args:
        writes: Fully rendered updates whose source state must be revalidated.
        template: Captured template when any selected write creates a daily note.

    Raises:
        SyncError: If a path resolves differently, content changed, an expected
            file disappeared, or a planned-new target appeared.
    """

    if template is not None:
        if template.path.resolve() != template.path:
            raise SyncError(
                f"Template path changed after preview: {template.path}"
            )
        try:
            current_template = template.path.read_bytes()
        except OSError as error:
            raise SyncError(
                f"Cannot revalidate template {template.path}: {error}"
            ) from error
        if current_template != template.data:
            raise SyncError(f"Template changed after preview: {template.path}")

    for write in writes:
        if write.path.resolve() != write.path:
            raise SyncError(f"Target path changed after preview: {write.path}")
        if write.original is None:
            if write.path.exists():
                raise SyncError(f"Target appeared after preview: {write.path}")
            continue
        try:
            current = write.path.read_bytes()
        except OSError as error:
            raise SyncError(
                f"Cannot revalidate {write.path}: {error}"
            ) from error
        if current != write.original.data:
            raise SyncError(f"Target changed after preview: {write.path}")


def apply_writes(
    writes: Sequence[PlannedWrite], template: FileSnapshot | None = None
) -> None:
    """Validate, stage, and atomically replace selected daily notes.

    Every complete output is written and flushed to a sibling temporary file with
    the intended permission bits. Snapshots are checked before staging and again
    immediately before replacement to narrow the race window. Replacement is
    atomic per file; the operation is not a transactional multi-file commit.

    Args:
        writes: Complete target contents produced from preview snapshots.
        template: Template snapshot required by selected creations, if any.

    Raises:
        SyncError: If validation, staging, permission changes, or replacement fails.
    """

    if not writes:
        return

    # Reject stale plans before doing even temporary-file work.
    validate_snapshots(writes, template)
    staged: list[tuple[Path, Path]] = []
    try:
        for write in writes:
            write.path.parent.mkdir(parents=True, exist_ok=True)
            descriptor, temporary_name = tempfile.mkstemp(
                prefix=f".{write.path.name}.",
                suffix=".tmp",
                dir=write.path.parent,
            )
            temporary = Path(temporary_name)
            try:
                with os.fdopen(descriptor, "wb") as stream:
                    stream.write(write.data)
                    stream.flush()
                    os.fsync(stream.fileno())
                os.chmod(temporary, write.mode)
            except BaseException:
                temporary.unlink(missing_ok=True)
                raise
            staged.append((temporary, write.path))

        # Recheck after staging to catch edits made during potentially slow I/O.
        validate_snapshots(writes, template)
        for temporary, target in staged:
            os.replace(temporary, target)
    except (OSError, SyncError) as error:
        raise SyncError(
            f"Could not apply daily-note updates: {error}"
        ) from error
    finally:
        for temporary, _ in staged:
            temporary.unlink(missing_ok=True)


def _parse_cli_date(value: str) -> date:
    """Parse an ISO calendar date for ``argparse``.

    Args:
        value: Expected ``YYYY-MM-DD`` command-line value.

    Returns:
        Parsed calendar date.

    Raises:
        argparse.ArgumentTypeError: If ``value`` is not a valid ISO date.
    """

    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            f"invalid ISO date: {value!r}"
        ) from error


def _parse_year(value: str) -> int:
    """Parse a four-digit calendar year for ``argparse``.

    Args:
        value: Exactly four decimal digits.

    Returns:
        Year in the range supported by ``datetime.date``.

    Raises:
        argparse.ArgumentTypeError: If syntax or range is invalid.
    """

    if not re.fullmatch(r"\d{4}", value):
        raise argparse.ArgumentTypeError(
            "year must contain exactly four digits"
        )
    year = int(value)
    if not 1 <= year <= 9999:
        raise argparse.ArgumentTypeError("year must be between 0001 and 9999")
    return year


def build_argument_parser() -> argparse.ArgumentParser:
    """Create the command-line interface without parsing process state.

    Returns:
        Parser defining vault/configuration overrides, date bounds, selector
        choice, and non-interactive approval.
    """

    parser = argparse.ArgumentParser(
        description=(
            "Preview and add missing unique-note wikilinks to Obsidian daily notes."
        )
    )
    parser.add_argument(
        "--vault",
        type=Path,
        default=Path.cwd(),
        help="vault root (default: current directory)",
    )
    parser.add_argument(
        "--daily-template",
        help="daily-note template path, relative to the vault by default",
    )
    parser.add_argument(
        "--daily-notes-root",
        help="daily-note root directory, relative to the vault by default",
    )
    parser.add_argument(
        "--daily-notes-format",
        help="daily path format using YYYY, MM, DD, and bracketed literals",
    )
    parser.add_argument(
        "--selector",
        choices=("auto", "fzf", "questionary", "text"),
        default="auto",
        help="interactive selector backend (default: auto)",
    )
    parser.add_argument(
        "--year", type=_parse_year, help="scan one calendar year"
    )
    parser.add_argument(
        "--start", type=_parse_cli_date, help="inclusive start date"
    )
    parser.add_argument(
        "--end", type=_parse_cli_date, help="inclusive end date"
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="approve every eligible insertion without prompting",
    )
    return parser


def _date_bounds(
    args: argparse.Namespace, parser: argparse.ArgumentParser
) -> tuple[date | None, date | None]:
    """Validate mutually exclusive CLI date filters and derive bounds.

    Args:
        args: Namespace returned by the command's argument parser.
        parser: Parser used to emit consistent usage errors.

    Returns:
        Inclusive start and end dates, each ``None`` when no filter was supplied.

    Raises:
        SystemExit: Through ``parser.error`` when filter combinations are invalid.
    """

    if args.year is not None and (
        args.start is not None or args.end is not None
    ):
        parser.error("--year cannot be combined with --start or --end")
    if (args.start is None) != (args.end is None):
        parser.error("--start and --end must be supplied together")
    if args.start is not None and args.start > args.end:
        parser.error("--start must not be later than --end")
    if args.year is not None:
        return date(args.year, 1, 1), date(args.year, 12, 31)
    return args.start, args.end


def main(
    argv: Sequence[str] | None = None,
    *,
    input_stream: TextIO | None = None,
    output: TextIO | None = None,
    error_output: TextIO | None = None,
) -> int:
    """Run preview, confirmation, and guarded synchronization phases.

    Args:
        argv: Arguments excluding the executable name, or ``None`` for
            ``sys.argv``.
        input_stream: Optional interactive-input replacement, primarily for tests.
        output: Optional standard-output replacement.
        error_output: Optional standard-error replacement.

    Returns:
        ``0`` for success or safe no-op, ``1`` for configuration/I/O failures, and
        ``2`` when confirmation is required but input is non-interactive.
    """

    input_stream = sys.stdin if input_stream is None else input_stream
    output = sys.stdout if output is None else output
    error_output = sys.stderr if error_output is None else error_output
    parser = build_argument_parser()
    args = parser.parse_args(argv)
    start, end = _date_bounds(args, parser)
    vault = args.vault.expanduser().resolve()
    if not vault.is_dir():
        print(f"Error: vault is not a directory: {vault}", file=error_output)
        return 1

    # Discovery and preview planning are read-only; no target can change in this phase.
    try:
        config = resolve_daily_note_config(
            vault,
            daily_notes_root=args.daily_notes_root,
            daily_template=args.daily_template,
            daily_notes_format=args.daily_notes_format,
        )
        candidates, discovery_warnings = discover_unique_notes(
            vault, start, end
        )
        daily_notes = discover_daily_notes(config)
        classification = classify_notes(config, candidates, daily_notes)
        groups, target_warnings, template = prepare_proposal_groups(
            config, classification.proposals, daily_notes
        )
    except SyncError as error:
        print(f"Error: {error}", file=error_output)
        return 1

    warnings = (*discovery_warnings, *target_warnings)
    print_preview(vault, candidates, classification, groups, warnings, output)

    if not groups:
        print("\nNo eligible changes.", file=output)
        return 0

    if args.yes:
        selected_ids = parse_selection("all", groups)
    else:
        is_interactive = getattr(input_stream, "isatty", lambda: False)()
        if not is_interactive:
            print(
                "Error: interactive confirmation requires a terminal; rerun with --yes.",
                file=error_output,
            )
            return 2
        try:
            selected_ids = choose_selection(
                groups, args.selector, input_stream, output
            )
        except SyncError as error:
            print(f"Error: {error}", file=error_output)
            return 1

    if not selected_ids:
        print("\nNo changes selected.", file=output)
        return 0

    # Only an explicit selection crosses the boundary from preview to mutation.
    writes = build_planned_writes(groups, selected_ids)
    try:
        apply_writes(
            writes,
            template
            if any(write.original is None for write in writes)
            else None,
        )
    except SyncError as error:
        print(f"Error: {error}", file=error_output)
        return 1

    created = sum(write.original is None for write in writes)
    print(
        f"\nApplied {len(selected_ids)} links across {len(writes)} daily notes "
        f"({created} created, {len(writes) - created} updated).",
        file=output,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
