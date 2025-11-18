"""
Fix Tag Note Paths - Update path field in existing tag notes based on folder location
"""

import re
import yaml
from pathlib import Path
import sys


def fix_tag_note_path(tag_note_path: Path, vault_path: Path):
    """Fix the path field in a tag note's frontmatter"""

    # Read content
    content = tag_note_path.read_text(encoding='utf-8')

    # Extract frontmatter
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        print(f"[!] No frontmatter in {tag_note_path.name}")
        return False

    frontmatter_text = match.group(1)
    frontmatter = yaml.safe_load(frontmatter_text)

    # Get current path value
    current_path = frontmatter.get('path', 'Unknown')

    # Calculate correct path from file location
    relative_path = tag_note_path.parent.relative_to(vault_path)
    folder_parts = list(relative_path.parts)

    # Get tag name (filename without .md)
    tag_name = tag_note_path.stem

    # Build full taxonomy path
    if folder_parts and folder_parts[0] not in ['30-Resources']:
        # Use actual folder structure
        full_path_parts = folder_parts + [tag_name]
        new_path = ' > '.join(full_path_parts)
        root = folder_parts[0]
    else:
        # Fallback
        new_path = f"Resources > {tag_name}"
        root = "Resources"

    # Update if changed
    if current_path != new_path:
        frontmatter['path'] = new_path
        frontmatter['root'] = root

        # Replace frontmatter
        new_frontmatter = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True).strip()
        new_content = content.replace(
            f'---\n{frontmatter_text}\n---',
            f'---\n{new_frontmatter}\n---'
        )

        tag_note_path.write_text(new_content, encoding='utf-8')

        print(f"[+] {tag_note_path.name}")
        print(f"    Old: {current_path}")
        print(f"    New: {new_path}")
        return True
    else:
        print(f"[-] {tag_note_path.name} - Already correct")
        return False


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Fix path fields in tag notes")
    parser.add_argument("--vault", type=str, required=True, help="Path to Obsidian vault")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be fixed without making changes")

    args = parser.parse_args()

    vault_path = Path(args.vault)
    if not vault_path.exists():
        print(f"[X] Vault not found: {vault_path}")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"Fix Tag Note Paths")
    if args.dry_run:
        print(f"Mode: DRY RUN")
    print(f"{'='*60}\n")

    # Find all tag notes
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

    print(f"[i] Found {len(tag_notes)} tag note(s)\n")

    if args.dry_run:
        for tag_note in tag_notes:
            # Just show what would change
            relative_path = tag_note.parent.relative_to(vault_path)
            folder_parts = list(relative_path.parts)
            tag_name = tag_note.stem

            if folder_parts and folder_parts[0] not in ['30-Resources']:
                full_path_parts = folder_parts + [tag_name]
                new_path = ' > '.join(full_path_parts)
            else:
                new_path = f"Resources > {tag_name}"

            print(f"[~] {tag_note.name} -> {new_path}")

        print(f"\n[i] Dry run complete")
        return

    # Fix all tag notes
    fixed_count = 0
    for tag_note in tag_notes:
        if fix_tag_note_path(tag_note, vault_path):
            fixed_count += 1

    print(f"\n{'='*60}")
    print(f"[+] Complete: {fixed_count}/{len(tag_notes)} tag notes updated")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
