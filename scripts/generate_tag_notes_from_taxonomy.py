#!/usr/bin/env python3
"""
Generate Tag Notes from Taxonomy

Creates tag note files for ALL tags defined in taxonomy that don't have corresponding notes yet.
This populates the knowledge graph with proper hierarchy and connections.

CRITICAL: Each tag note MUST have tags: [tag-name] in frontmatter to merge hashtag with note file.
"""

import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
import sys

try:
    from scripts.tag_path_resolver import TagPathResolver
except ImportError:
    from tag_path_resolver import TagPathResolver


class TaxonomyTagNoteGenerator:
    """Generate tag notes from taxonomy definitions"""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.resolver = TagPathResolver(self.vault_path)
        self.taxonomy = self.resolver.taxonomy

        self.stats = {
            'created': 0,
            'skipped': 0,
            'errors': 0
        }

    def determine_file_path(self, tag: str, tax_data: Dict) -> Path:
        """
        Determine where tag note file should be saved based on taxonomy path

        Args:
            tag: Tag identifier
            tax_data: Taxonomy data for tag

        Returns:
            Full file path for tag note
        """
        path = tax_data.get('path', '')
        canonical = tax_data.get('canonical', tag.replace('-', ' ').title())

        if not path:
            # Fallback to Resources
            folder = self.vault_path / "30-Resources" / "knowledge"
        else:
            # Parse path to build folder structure
            parts = [p.strip() for p in path.split('>')]

            # Build folder path
            # Example: "Technology > Programming > Languages > Python"
            # Results in: Technology/Programming/Languages/
            if len(parts) > 1:
                folder = self.vault_path / parts[0]
                for part in parts[1:-1]:  # All except first and last
                    folder = folder / part
            else:
                folder = self.vault_path / parts[0]

        # Ensure folder exists
        folder.mkdir(parents=True, exist_ok=True)

        # Use canonical name for filename
        filename = canonical.replace('/', '-').replace('\\', '-') + '.md'

        return folder / filename

    def create_tag_note(self, tag: str, tax_data: Dict, dry_run: bool = False) -> bool:
        """
        Create a single tag note from taxonomy data

        Args:
            tag: Tag identifier
            tax_data: Taxonomy data
            dry_run: If True, only show what would be created

        Returns:
            True if created, False if skipped or error
        """
        try:
            canonical = tax_data.get('canonical', tag.replace('-', ' ').title())
            file_path = self.determine_file_path(tag, tax_data)

            # Check if already exists
            if file_path.exists():
                print(f"[SKIP] {canonical} - already exists")
                self.stats['skipped'] += 1
                return False

            # Extract metadata
            parent_tags = tax_data.get('parent_tags', [])
            root = tax_data.get('root', 'Resources')
            path = tax_data.get('path', f'{root} > {canonical}')
            depth = tax_data.get('depth', 1)
            description = tax_data.get('description', '')

            # Build frontmatter
            frontmatter = {
                'type': 'tag-note',
                'tags': [tag],  # 🔥 CRITICAL: Merges hashtag with note file
                'tag': tag,
                'canonical': canonical,
                'root': root,
                'path': path,
                'parent_tags': parent_tags,
                'depth': depth,
                'created': datetime.now().strftime('%Y-%m-%d'),
                'last_updated': datetime.now().strftime('%Y-%m-%d'),
                'total_conversations': 0,
                'total_time_minutes': 0
            }

            # Generate hierarchy section if parent tags exist
            hierarchy_section = ""
            if parent_tags:
                # Get canonical names for parent tags
                parent_links = []
                for parent in parent_tags:
                    parent_canonical = self.taxonomy.get(parent, {}).get('canonical', parent.replace('-', ' ').title())
                    parent_links.append(f'[[{parent_canonical}]]')

                parent_chain = ' > '.join(parent_links)
                hierarchy_section = f"""
## Hierarchy
**Parent Categories**: {parent_chain}

"""

            # Build content
            current_month = datetime.now().strftime('%B %Y')

            understanding = description if description else "*To be developed through conversations*"

            content = f"""---
{yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True).strip()}
---

# {canonical}
{hierarchy_section}
## Current Understanding
{understanding}

## {current_month}

"""

            if dry_run:
                print(f"[DRY RUN] Would create: {file_path.relative_to(self.vault_path)}")
                print(f"    Parents: {', '.join(parent_tags) if parent_tags else 'None'}")
                print(f"    Depth: {depth}")
                return True

            # Write file
            file_path.write_text(content, encoding='utf-8')

            print(f"[CREATE] {canonical}")
            print(f"    Path: {file_path.relative_to(self.vault_path)}")
            print(f"    Parents: {', '.join(parent_tags) if parent_tags else 'None'}")

            self.stats['created'] += 1
            return True

        except Exception as e:
            print(f"[ERROR] {canonical}: {e}")
            self.stats['errors'] += 1
            return False

    def generate_all(self, dry_run: bool = False, filter_root: str = None):
        """
        Generate tag notes for all taxonomy entries

        Args:
            dry_run: If True, only show what would be created
            filter_root: If provided, only generate for this root (e.g., "Language")
        """
        print(f"\n{'='*60}")
        print(f"Generate Tag Notes from Taxonomy")
        if dry_run:
            print(f"Mode: DRY RUN")
        if filter_root:
            print(f"Filter: Only {filter_root} root")
        print(f"{'='*60}\n")

        print(f"[i] Taxonomy contains {len(self.taxonomy)} tags\n")

        # Filter if requested
        tags_to_process = []
        for tag, tax_data in sorted(self.taxonomy.items()):
            if filter_root and tax_data.get('root') != filter_root:
                continue

            tags_to_process.append((tag, tax_data))

        print(f"[i] Processing {len(tags_to_process)} tags\n")

        # Generate each tag note
        for tag, tax_data in tags_to_process:
            self.create_tag_note(tag, tax_data, dry_run=dry_run)

        # Print summary
        print(f"\n{'='*60}")
        print(f"[+] Complete")
        print(f"    Created: {self.stats['created']}")
        print(f"    Skipped: {self.stats['skipped']}")
        print(f"    Errors: {self.stats['errors']}")
        print(f"{'='*60}\n")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate tag notes from taxonomy")
    parser.add_argument("--vault", type=str, required=True, help="Path to Obsidian vault")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be created without making changes")
    parser.add_argument("--root", type=str, help="Only generate tags for specific root (e.g., 'Language', 'Technology')")

    args = parser.parse_args()

    vault_path = Path(args.vault)
    if not vault_path.exists():
        print(f"[X] Vault not found: {vault_path}")
        sys.exit(1)

    generator = TaxonomyTagNoteGenerator(str(vault_path))
    generator.generate_all(dry_run=args.dry_run, filter_root=args.root)


if __name__ == "__main__":
    main()
