#!/usr/bin/env python3
"""
Add Hashtags to Tag Notes - Backfill existing tag notes with tags: field

🔥 CRITICAL: This script ensures all tag notes have tags: [tag-name] in frontmatter,
which merges the hashtag node with the note file node in Obsidian graph view.

Without this, conversations and tag notes appear as separate duplicate nodes.
"""

import re
import yaml
from pathlib import Path
import sys


def add_hashtag_to_tag_note(tag_note_path: Path, vault_path: Path) -> bool:
    """
    Add tags: field to tag note frontmatter if missing

    Args:
        tag_note_path: Path to tag note file
        vault_path: Path to vault root

    Returns:
        True if modified, False if skipped
    """
    try:
        # Read content
        content = tag_note_path.read_text(encoding='utf-8')

        # Extract frontmatter
        match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not match:
            print(f"[!] No frontmatter in {tag_note_path.name}")
            return False

        frontmatter_text = match.group(1)
        frontmatter = yaml.safe_load(frontmatter_text)

        # Check if tags field already exists
        if 'tags' in frontmatter and frontmatter['tags']:
            print(f"[-] {tag_note_path.name} - already has tags field")
            return False

        # Get tag identifier
        tag_id = frontmatter.get('tag')
        if not tag_id:
            print(f"[!] {tag_note_path.name} - no tag field in frontmatter")
            return False

        # 🔥 CRITICAL: Add tags field
        frontmatter['tags'] = [tag_id]

        # Regenerate frontmatter YAML
        new_frontmatter = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True, sort_keys=False).strip()

        # Replace frontmatter in content
        new_content = content.replace(
            f'---\n{frontmatter_text}\n---',
            f'---\n{new_frontmatter}\n---'
        )

        # Write back
        tag_note_path.write_text(new_content, encoding='utf-8')

        print(f"[+] {tag_note_path.name}")
        print(f"    Added: tags: [{tag_id}]")

        return True

    except Exception as e:
        print(f"[ERROR] {tag_note_path.name}: {e}")
        return False


def find_tag_notes(vault_path: Path) -> list[Path]:
    """Find all tag note files in vault"""
    tag_notes = []

    for md_file in vault_path.rglob("*.md"):
        # Skip certain directories
        if any(part in md_file.parts for part in ["00-Inbox", "_system", ".obsidian"]):
            continue

        # Check if it's a tag note
        try:
            content = md_file.read_text(encoding='utf-8')
            if 'type: tag-note' in content[:500]:
                tag_notes.append(md_file)
        except Exception as e:
            pass

    return tag_notes


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Add hashtag field to existing tag notes")
    parser.add_argument("--vault", type=str, required=True, help="Path to Obsidian vault")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be modified without making changes")

    args = parser.parse_args()

    vault_path = Path(args.vault)
    if not vault_path.exists():
        print(f"[X] Vault not found: {vault_path}")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"Add Hashtags to Tag Notes (CRITICAL)")
    if args.dry_run:
        print(f"Mode: DRY RUN")
    print(f"{'='*60}\n")

    # Find all tag notes
    tag_notes = find_tag_notes(vault_path)
    print(f"[i] Found {len(tag_notes)} tag note(s)\n")

    if not tag_notes:
        print("[!] No tag notes found")
        return

    # Process each
    modified = 0
    skipped = 0

    for tag_note in tag_notes:
        if args.dry_run:
            # Read to check
            content = tag_note.read_text(encoding='utf-8')
            match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
            if match:
                fm = yaml.safe_load(match.group(1))
                tag_id = fm.get('tag', '?')
                has_tags = 'tags' in fm and fm['tags']

                if not has_tags:
                    print(f"[DRY RUN] Would add: tags: [{tag_id}] to {tag_note.name}")
                    modified += 1
                else:
                    skipped += 1
        else:
            if add_hashtag_to_tag_note(tag_note, vault_path):
                modified += 1
            else:
                skipped += 1

    print(f"\n{'='*60}")
    print(f"[+] Complete")
    print(f"    Modified: {modified}")
    print(f"    Skipped: {skipped}")
    print(f"{'='*60}\n")

    if not args.dry_run and modified > 0:
        print(f"[SUCCESS] {modified} tag notes updated with hashtag field!")
        print(f"[INFO] Reload Obsidian graph view to see merged nodes")


if __name__ == "__main__":
    main()
