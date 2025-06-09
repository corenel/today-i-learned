"""
A command-line utility for parsing Obsidian-style wiki-links from a markdown file,
locating the linked files within a specified vault directory, and aggregating
their contents into a single markdown file.

This script is designed to help consolidate notes, research, or any related
markdown documents into a single, cohesive file for easier reading, sharing, or
processing. It correctly handles various wiki-link formats, including aliases
and header links, ensuring that only the file content is extracted.

Key Features:
- Extracts unique wiki-links from a primary markdown file.
- Recursively searches a vault directory to find the linked files.
- Handles link aliases ([[filename|alias]]) and header links ([[filename#header]]).
- Aggregates the content of all found files into a specified output file.
- Provides verbose logging for detailed process tracking.

Usage:
    python .tools/aggregate_wikilinks.py --input-file <INPUT_MD> --vault-dir <VAULT_PATH> --output-file <OUTPUT_MD>
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Optional, Set

from loguru import logger

# This regex is designed to capture the full inner content of a wiki-link.
# It's the first step in parsing all link variations.
WIKI_LINK_REGEX = re.compile(r"\[\[([^\]]+)\]\]")


def parse_arguments() -> argparse.Namespace:
    """
    Sets up and parses command-line arguments.

    This function defines the command-line interface for the script,
    including required arguments for input file, vault directory, and output file,
    as well as an optional flag for verbose logging.

    Returns:
        An argparse.Namespace object containing the parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Extracts linked files from an Obsidian vault based on a markdown file and aggregates their contents.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Example Usage:
  python aggregate_links.py \\
    --input-file "My Project Note.md" \\
    --vault-dir "/path/to/your/obsidian/vault" \\
    --output-file "project_summary.md"
""",
    )
    parser.add_argument(
        "--input-file",
        type=Path,
        required=True,
        help="Path to the initial markdown file containing the wiki-links.",
    )
    parser.add_argument(
        "--vault-dir",
        type=Path,
        required=True,
        help="Path to the root directory of the Obsidian vault to search recursively.",
    )
    parser.add_argument(
        "--output-file",
        type=Path,
        required=True,
        help="Path to the output file where aggregated contents will be saved.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose (DEBUG) logging for more detailed output.",
    )
    return parser.parse_args()


def extract_wiki_links(file_path: Path) -> List[str]:
    """
    Extracts all unique, valid wiki-link targets from a markdown file.

    This function reads a markdown file and uses a regular expression to find all
    Obsidian-style wiki-links. It then processes these links to handle various
    formats, ensuring that only the core file reference is extracted.

    Supported formats:
    - [[My Note]] -> "My Note"
    - [[My Note|Some Alias]] -> "My Note"
    - [[My Note#A Header]] -> "My Note"

    Links that only point to headers within the same file (e.g., [[#A Header]])
    are ignored, as they do not reference external files. The extracted link
    targets are returned as a unique, sorted list of strings.

    Args:
        file_path: The `Path` object of the markdown file to parse.

    Returns:
        A sorted list of unique file basenames (without the .md extension)
        extracted from the wiki-links. Returns an empty list if the file
        cannot be read or contains no valid links.
    """
    if not file_path.is_file():
        logger.error(f"Input file not found: {file_path}")
        return []

    logger.info(f"Extracting links from: {file_path}")
    try:
        content = file_path.read_text(encoding="utf-8")
        raw_targets: List[str] = WIKI_LINK_REGEX.findall(content)

        processed_links: Set[str] = set()
        for target in raw_targets:
            # Get the part before any alias (|) or header/block ref (#)
            file_basename = target.split("|")[0].split("#")[0]

            # Ignore empty links or links that only point to a header in the current file
            if file_basename:
                processed_links.add(file_basename.strip())

        unique_links = sorted(list(processed_links))
        logger.success(f"Found {len(unique_links)} unique file links.")
        logger.debug(f"File links found: {unique_links}")
        return unique_links
    except Exception as e:
        logger.error(f"Failed to read or parse {file_path}: {e}")
        return []


def find_file_in_vault(vault_dir: Path, file_basename: str) -> Optional[Path]:
    """
    Recursively searches for a markdown file in the vault by its basename.

    This function attempts to find a file named `{file_basename}.md` within the
    specified `vault_dir`. The search is recursive, scanning all subdirectories.

    If multiple files with the same name exist, this function will log a warning
    and return the first match found. This mirrors a simplified version of
    `rglob`'s behavior, which may not be deterministic. Obsidian has its own
    internal logic for handling such conflicts which is not replicated here.

    Args:
        vault_dir: The root `Path` of the vault directory to search within.
        file_basename: The name of the file to find, without the `.md` extension.

    Returns:
        A `Path` object pointing to the first found file, or `None` if no
        matching file is found.
    """
    target_filename = f"{file_basename}.md"
    logger.debug(f"Searching for file: {target_filename!r} in vault: {vault_dir}")

    # Use rglob for a recursive search. It's efficient as it returns a generator.
    try:
        found_files = list(vault_dir.rglob(target_filename))
    except Exception as e:
        logger.error(f"Error while searching for {target_filename!r}: {e}")
        return None

    if not found_files:
        logger.warning(f"File not found for link: [[{file_basename}]]")
        return None

    if len(found_files) > 1:
        # Obsidian has its own logic for resolving duplicates.
        # For simplicity, we'll use the first one found and warn the user.
        logger.warning(
            f"Multiple files found for [[{file_basename}]]. Using the first one: {found_files[0]}"
        )
        logger.debug(f"All found paths: {[str(p) for p in found_files]}")

    return found_files[0]


def main() -> None:
    """
    The main entry point for the script.

    This function orchestrates the entire process:
    1. Parses command-line arguments.
    2. Configures logging based on verbosity settings.
    3. Validates that the input file and vault directory exist.
    4. Ensures the output directory can be created.
    5. Extracts wiki-links from the input file.
    6. Iterates through each link, finds the corresponding file in the vault,
       and reads its content.
    7. Aggregates the contents of all found files.
    8. Writes the final aggregated content to the specified output file.
    """
    args = parse_arguments()

    # Configure logger based on verbosity
    logger.remove()
    log_level = "DEBUG" if args.verbose else "INFO"
    logger.add(
        sys.stderr,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    )

    # --- Path Validations ---
    if not args.input_file.is_file():
        logger.critical(f"Input file does not exist: {args.input_file}")
        sys.exit(1)
    if not args.vault_dir.is_dir():
        logger.critical(f"Vault directory does not exist: {args.vault_dir}")
        sys.exit(1)

    # Ensure output directory exists before writing
    try:
        args.output_file.parent.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        logger.critical(f"Could not create output directory {args.output_file.parent}: {e}")
        sys.exit(1)

    # --- Core Logic ---
    links = extract_wiki_links(args.input_file)
    if not links:
        logger.warning("No links found in the input file. Output will be empty.")
        args.output_file.touch()
        sys.exit(0)

    aggregated_contents = []
    found_count = 0
    for link_basename in links:
        logger.info(f"Processing link: [[{link_basename}]]")
        linked_file_path = find_file_in_vault(args.vault_dir, link_basename)

        if linked_file_path:
            logger.success(f"Found file at: {linked_file_path.relative_to(args.vault_dir)}")
            try:
                content = linked_file_path.read_text(encoding="utf-8")
                # Add a separator and a title for clarity in the aggregated file
                header = f"\n\n---\n\n# Source: [[{link_basename}]]\n\n"
                aggregated_contents.append(header + content)
                found_count += 1
            except Exception as e:
                logger.error(f"Could not read content from {linked_file_path}: {e}")

    # --- Write Output ---
    if not aggregated_contents:
        logger.warning("No linked files were found or could be read. Output file will be empty.")
        final_content = ""
    else:
        logger.info(f"Successfully processed and aggregated {found_count} of {len(links)} linked files.")
        # Join all content, stripping any leading whitespace from the first file.
        final_content = "".join(aggregated_contents).lstrip()

    try:
        args.output_file.write_text(final_content, encoding="utf-8")
        logger.success(f"Aggregated content successfully written to: {args.output_file}")
    except Exception as e:
        logger.critical(f"Failed to write to output file {args.output_file}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
