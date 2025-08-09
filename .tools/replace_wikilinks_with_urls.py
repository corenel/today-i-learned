"""
A command-line utility for replacing Obsidian-style wiki-links with standard
markdown links, where the URLs are extracted from the metadata of linked files.

This script processes markdown files containing wiki-links ([[xxx]]) and replaces
them with standard markdown links ([xxx](url)), where the URL is extracted from
the YAML frontmatter of the linked file.

Supported metadata formats:
1. source: field (e.g., xiaobot links)
2. url: field (e.g., arxiv links)

Key Features:
- Extracts wiki-links from a markdown file
- Locates linked files within a vault directory
- Parses YAML frontmatter to extract URLs
- Replaces wiki-links with standard markdown links
- Preserves original link text
- Falls back to wiki-link format if no URL is found
- Handles link aliases and header links

Usage:
    python .tools/replace_wikilinks_with_urls.py --input-file <INPUT_MD> --vault-dir <VAULT_PATH> --output-file <OUTPUT_MD>
"""

import argparse
import re
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from loguru import logger

# Regex to capture wiki-links
WIKI_LINK_REGEX = re.compile(r"\[\[([^\]]+)\]\]")

# Regex to extract YAML frontmatter
YAML_FRONTMATTER_REGEX = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL | re.MULTILINE)


def parse_arguments() -> argparse.Namespace:
    """
    Sets up and parses command-line arguments.

    Returns:
        An argparse.Namespace object containing the parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Replaces wiki-links with standard markdown links using URLs from file metadata.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Example Usage:
  python replace_wikilinks_with_urls.py \\
    --input-file "My Note.md" \\
    --vault-dir "/path/to/obsidian/vault" \\
    --output-file "processed_note.md"
""",
    )
    parser.add_argument(
        "--input-file",
        type=Path,
        required=True,
        help="Path to the markdown file containing wiki-links to replace.",
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
        help="Path to the output file where the processed content will be saved.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose (DEBUG) logging for more detailed output.",
    )
    return parser.parse_args()


def extract_url_from_metadata(file_path: Path) -> Optional[str]:
    """
    Extracts the URL from the YAML frontmatter of a markdown file.

    Looks for 'source:', 'url:', or 'link:' fields in the frontmatter.
    If none are found, attempts to find the first URL-like value in any field.

    Args:
        file_path: The Path object of the markdown file to parse.

    Returns:
        The extracted URL as a string, or None if no URL is found.
    """
    if not file_path.is_file():
        logger.warning(f"File not found: {file_path}")
        return None

    try:
        content = file_path.read_text(encoding="utf-8")
        match = YAML_FRONTMATTER_REGEX.match(content)

        if not match:
            logger.debug(f"No YAML frontmatter found in: {file_path}")
            return None

        yaml_content = match.group(1)

        try:
            metadata = yaml.safe_load(yaml_content)
            if not isinstance(metadata, dict):
                logger.debug(f"Invalid YAML structure in: {file_path}")
                return None

            # Check for specific URL fields in priority order
            url = metadata.get('source') or metadata.get('url') or metadata.get('link')

            if url:
                logger.debug(f"Found URL '{url}' in specific field in {file_path}")
                return str(url)

            # Fallback: search for first URL-like value in any field
            logger.debug(f"No specific URL field found, searching for URL-like values in {file_path}")
            url_pattern = re.compile(r'^https?://', re.IGNORECASE)

            def find_url_in_value(value):
                """Recursively search for URL-like strings in metadata values."""
                if isinstance(value, str) and url_pattern.match(value):
                    return value
                elif isinstance(value, list):
                    for item in value:
                        found_url = find_url_in_value(item)
                        if found_url:
                            return found_url
                elif isinstance(value, dict):
                    for v in value.values():
                        found_url = find_url_in_value(v)
                        if found_url:
                            return found_url
                return None

            for key, value in metadata.items():
                found_url = find_url_in_value(value)
                if found_url:
                    logger.debug(f"Found URL '{found_url}' in field '{key}' in {file_path}")
                    return found_url

            logger.debug(f"No URL found in metadata of: {file_path}")
            return None

        except yaml.YAMLError as e:
            logger.warning(f"Failed to parse YAML in {file_path}: {e}")
            return None

    except Exception as e:
        logger.error(f"Failed to read {file_path}: {e}")
        return None


def find_file_in_vault(vault_dir: Path, file_basename: str) -> Optional[Path]:
    """
    Recursively searches for a markdown file in the vault by its basename.

    Args:
        vault_dir: The root Path of the vault directory to search within.
        file_basename: The name of the file to find, without the .md extension.

    Returns:
        A Path object pointing to the first found file, or None if no
        matching file is found.
    """
    target_filename = f"{file_basename}.md"
    logger.debug(f"Searching for file: {target_filename!r} in vault: {vault_dir}")

    try:
        found_files = list(vault_dir.rglob(target_filename))
    except Exception as e:
        logger.error(f"Error while searching for {target_filename!r}: {e}")
        return None

    if not found_files:
        logger.warning(f"File not found for link: [[{file_basename}]]")
        return None

    if len(found_files) > 1:
        logger.warning(
            f"Multiple files found for [[{file_basename}]]. Using the first one: {found_files[0]}"
        )
        logger.debug(f"All found paths: {[str(p) for p in found_files]}")

    return found_files[0]


def build_link_url_map(content: str, vault_dir: Path) -> Dict[str, Tuple[str, Optional[str]]]:
    """
    Builds a mapping of wiki-links to their replacement URLs.

    For each wiki-link found in the content, this function:
    1. Extracts the file basename (handling aliases and headers)
    2. Finds the corresponding file in the vault
    3. Extracts the URL from the file's metadata
    4. Maps the original link to its replacement

    Args:
        content: The markdown content containing wiki-links.
        vault_dir: The root Path of the vault directory.

    Returns:
        A dictionary mapping original wiki-link content to tuples of
        (display_text, url). If no URL is found, url will be None.
    """
    link_map = {}
    wiki_links = WIKI_LINK_REGEX.findall(content)

    for link_content in wiki_links:
        # Skip if we've already processed this exact link
        if link_content in link_map:
            continue

        # Extract the file basename and display text
        # Handle aliases: [[file|alias]] -> file, alias
        # Handle headers: [[file#header]] -> file, file
        parts = link_content.split("|")
        if len(parts) == 2:
            file_part, display_text = parts[0].strip(), parts[1].strip()
        else:
            file_part = link_content
            display_text = link_content

        # Remove header references from file part
        file_basename = file_part.split("#")[0].strip()

        # If no file basename (e.g., just [[#header]]), skip
        if not file_basename:
            logger.debug(f"Skipping header-only link: [[{link_content}]]")
            link_map[link_content] = (display_text, None)
            continue

        # Find the file and extract URL
        logger.info(f"Processing link: [[{link_content}]]")
        linked_file = find_file_in_vault(vault_dir, file_basename)

        if linked_file:
            url = extract_url_from_metadata(linked_file)
            if url:
                logger.success(f"Found URL for [[{file_basename}]]: {url}")
                link_map[link_content] = (display_text, url)
            else:
                logger.info(f"No URL found in metadata for [[{file_basename}]]")
                link_map[link_content] = (display_text, None)
        else:
            link_map[link_content] = (display_text, None)

    return link_map


def replace_wikilinks(content: str, link_map: Dict[str, Tuple[str, Optional[str]]]) -> str:
    """
    Replaces wiki-links in the content with standard markdown links.

    Args:
        content: The original markdown content.
        link_map: Dictionary mapping wiki-link content to (display_text, url) tuples.

    Returns:
        The processed content with wiki-links replaced.
    """
    def replace_link(match):
        link_content = match.group(1)
        if link_content in link_map:
            display_text, url = link_map[link_content]
            if url:
                # Replace with standard markdown link
                return f"[{display_text}]({url})"
            else:
                # Keep original wiki-link if no URL found
                return match.group(0)
        else:
            # Keep original if not in map (shouldn't happen)
            return match.group(0)

    processed_content = WIKI_LINK_REGEX.sub(replace_link, content)
    return processed_content


def main() -> None:
    """
    The main entry point for the script.
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

    # Path validations
    if not args.input_file.is_file():
        logger.critical(f"Input file does not exist: {args.input_file}")
        sys.exit(1)
    if not args.vault_dir.is_dir():
        logger.critical(f"Vault directory does not exist: {args.vault_dir}")
        sys.exit(1)

    # Ensure output directory exists
    try:
        args.output_file.parent.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        logger.critical(f"Could not create output directory {args.output_file.parent}: {e}")
        sys.exit(1)

    # Read input file
    logger.info(f"Reading input file: {args.input_file}")
    try:
        content = args.input_file.read_text(encoding="utf-8")
    except Exception as e:
        logger.critical(f"Failed to read input file: {e}")
        sys.exit(1)

    # Build link-to-URL mapping
    logger.info("Building link-to-URL mapping...")
    link_map = build_link_url_map(content, args.vault_dir)

    # Count statistics
    total_links = len(link_map)
    links_with_urls = sum(1 for _, (_, url) in link_map.items() if url is not None)

    logger.info(f"Found {total_links} unique wiki-links")
    logger.info(f"Successfully mapped {links_with_urls} links to URLs")

    # Replace wiki-links with standard markdown links
    logger.info("Replacing wiki-links...")
    processed_content = replace_wikilinks(content, link_map)

    # Write output
    try:
        args.output_file.write_text(processed_content, encoding="utf-8")
        logger.success(f"Processed content written to: {args.output_file}")
        logger.info(f"Replaced {links_with_urls}/{total_links} wiki-links with URLs")
    except Exception as e:
        logger.critical(f"Failed to write output file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
