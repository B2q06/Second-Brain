#!/usr/bin/env python3
"""
Tag Note Migration Script
Migrates existing tag notes from old flat schema to new hierarchical schema
"""

import re
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from logger_setup import get_logger, TimedOperation


class TagNoteMigrator:
    """Migrate tag notes to new hierarchical schema"""

    def __init__(self, vault_path: Path, taxonomy_path: Path = None):
        self.vault_path = Path(vault_path)
        self.logger = get_logger(__name__, str(vault_path))

        if taxonomy_path is None:
            taxonomy_path = self.vault_path / "_system" / "tag-taxonomy.md"

        self.taxonomy_path = Path(taxonomy_path)
        self.taxonomy = self._load_taxonomy()

    def _load_taxonomy(self) -> Dict:
        """Load taxonomy from tag-taxonomy.md"""
        self.logger.info(f"Loading taxonomy from {self.taxonomy_path}")

        if not self.taxonomy_path.exists():
            self.logger.error(f"Taxonomy file not found: {self.taxonomy_path}")
            return {}

        with open(self.taxonomy_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract YAML blocks
        taxonomy = {}
        yaml_blocks = re.findall(r'```yaml\n(.*?)\n```', content, re.DOTALL)

        for block in yaml_blocks:
            try:
                data = yaml.safe_load(block)
                if isinstance(data, dict):
                    taxonomy.update(data)
            except yaml.YAMLError as e:
                self.logger.warning(f"Failed to parse YAML block: {e}")

        self.logger.info(f"Loaded {len(taxonomy)} tags from taxonomy")
        return taxonomy

    def find_old_tag_notes(self) -> List[Path]:
        """Find all tag notes that need migration"""
        self.logger.info("Finding old tag notes")

        old_notes = []

        for md_file in self.vault_path.rglob("*.md"):
            if any(part in md_file.parts for part in ["00-Inbox", "_system", ".obsidian"]):
                continue

            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read(500)

                    # Check if it's a tag note
                    if 'type: tag-note' not in content:
                        continue

                    # Check if already migrated (has 'root:' field)
                    if 'root:' in content:
                        self.logger.debug(f"Already migrated: {md_file.name}")
                        continue

                    old_notes.append(md_file)
            except:
                pass

        self.logger.info(f"Found {len(old_notes)} tag notes to migrate")
        return old_notes

    def migrate_note(self, note_path: Path, dry_run: bool = False) -> bool:
        """Migrate a single tag note to new schema"""
        self.logger.info(f"Migrating: {note_path.name}")

        try:
            with open(note_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract frontmatter
            fm_match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
            if not fm_match:
                self.logger.error(f"No frontmatter found in {note_path.name}")
                return False

            frontmatter = fm_match.group(1)
            body = fm_match.group(2)

            # Parse frontmatter
            try:
                fm_data = yaml.safe_load(frontmatter)
            except yaml.YAMLError as e:
                self.logger.error(f"Failed to parse frontmatter in {note_path.name}: {e}")
                return False

            # Extract tag name
            tag = fm_data.get("tag", "")
            if not tag:
                self.logger.error(f"No tag field in {note_path.name}")
                return False

            # Look up in taxonomy
            if tag not in self.taxonomy:
                self.logger.warning(f"Tag '{tag}' not in taxonomy, skipping")
                return False

            tax_entry = self.taxonomy[tag]

            # Update frontmatter with new fields
            fm_data["canonical"] = tax_entry.get("canonical", tag)
            fm_data["parent_tags"] = tax_entry.get("parent_tags", [])
            fm_data["root"] = tax_entry.get("root", "Unknown")
            fm_data["path"] = tax_entry.get("path", f"{tax_entry.get('root', 'Unknown')} > {tag}")
            fm_data["depth"] = tax_entry.get("depth", 1)

            # Preserve existing fields
            if "last_updated" not in fm_data:
                fm_data["last_updated"] = datetime.now().strftime("%Y-%m-%d")

            # Generate new frontmatter YAML
            new_frontmatter = yaml.dump(fm_data, default_flow_style=False, allow_unicode=True, sort_keys=False)

            # Add hierarchy section to body if not present
            if "## Hierarchy" not in body and fm_data.get("parent_tags"):
                parent_tags = fm_data["parent_tags"]

                # Get canonical names for parent tags
                parent_links = []
                for parent in parent_tags:
                    parent_canonical = self.taxonomy.get(parent, {}).get('canonical', parent.replace('-', ' ').title())
                    parent_links.append(f'[[{parent_canonical}]]')

                parent_chain = ' > '.join(parent_links)
                hierarchy_section = f"\n## Hierarchy\n**Parent Categories**: {parent_chain}\n"

                # Insert after title (first # heading)
                lines = body.split('\n')
                title_index = next((i for i, line in enumerate(lines) if line.strip().startswith('# ')), 0)

                # Insert hierarchy section after title
                if title_index >= 0:
                    lines.insert(title_index + 1, hierarchy_section)
                    body = '\n'.join(lines)

            # Construct new content
            new_content = f"---\n{new_frontmatter}---\n{body}"

            if not dry_run:
                # Write back to file
                with open(note_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)

                self.logger.info(f"Successfully migrated: {note_path.name}")

                # Move to correct location based on taxonomy path
                new_location = self._determine_new_location(tag, tax_entry)
                if new_location and new_location != note_path.parent:
                    self._move_note(note_path, new_location, dry_run=False)

            else:
                self.logger.info(f"[DRY RUN] Would migrate: {note_path.name}")

            return True

        except Exception as e:
            self.logger.error(f"Failed to migrate {note_path.name}: {e}", exc_info=True)
            return False

    def _determine_new_location(self, tag: str, tax_entry: Dict) -> Optional[Path]:
        """Determine new folder location based on taxonomy path"""
        root = tax_entry.get("root", "Unknown")
        path = tax_entry.get("path", "")

        if not path:
            return None

        # Convert path to folder structure
        # Example: "Technology > Programming > Python" -> "Technology/Programming/"
        parts = [p.strip() for p in path.split(">")]

        if len(parts) <= 2:
            # Root level or one level deep
            folder = self.vault_path / parts[0]
        else:
            # Multi-level
            folder = self.vault_path / parts[0] / parts[1]

        return folder

    def _move_note(self, old_path: Path, new_folder: Path, dry_run: bool = False):
        """Move note to new location"""
        if not new_folder.exists() and not dry_run:
            new_folder.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Created folder: {new_folder}")

        new_path = new_folder / old_path.name

        if not dry_run:
            old_path.rename(new_path)
            self.logger.info(f"Moved: {old_path} -> {new_path}")
        else:
            self.logger.info(f"[DRY RUN] Would move: {old_path} -> {new_path}")

    def migrate_all(self, dry_run: bool = False) -> Dict[str, int]:
        """Migrate all old tag notes"""
        with TimedOperation(self.logger, "Tag note migration"):
            old_notes = self.find_old_tag_notes()

            stats = {
                "total": len(old_notes),
                "migrated": 0,
                "failed": 0,
                "skipped": 0
            }

            for note_path in old_notes:
                try:
                    success = self.migrate_note(note_path, dry_run=dry_run)
                    if success:
                        stats["migrated"] += 1
                    else:
                        stats["skipped"] += 1
                except Exception as e:
                    self.logger.error(f"Failed to migrate {note_path.name}: {e}")
                    stats["failed"] += 1

            self.logger.info(f"Migration complete: {stats['migrated']} migrated, {stats['skipped']} skipped, {stats['failed']} failed")

            return stats

    def create_missing_areas(self):
        """Create missing area folders based on taxonomy"""
        self.logger.info("Creating missing area folders")

        areas = set()

        for tag, tax_entry in self.taxonomy.items():
            path = tax_entry.get("path", "")
            if not path:
                continue

            parts = [p.strip() for p in path.split(">")]

            if len(parts) <= 2:
                folder = self.vault_path / parts[0]
            else:
                folder = self.vault_path / parts[0] / parts[1]

            areas.add(folder)

        for area in areas:
            if not area.exists():
                area.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"Created area folder: {area}")

    def generate_migration_report(self) -> str:
        """Generate migration report"""
        old_notes = self.find_old_tag_notes()

        report = f"# Tag Note Migration Report\n\n"
        report += f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        report += f"## Summary\n\n"
        report += f"- **Total tag notes found**: {len(old_notes)}\n"
        report += f"- **Tags in taxonomy**: {len(self.taxonomy)}\n\n"

        report += f"## Tag Notes to Migrate\n\n"

        for note_path in old_notes:
            try:
                with open(note_path, 'r', encoding='utf-8') as f:
                    content = f.read(500)

                tag_match = re.search(r'^tag:\s*(.+)$', content, re.MULTILINE)
                if tag_match:
                    tag = tag_match.group(1).strip()
                    in_taxonomy = "✅" if tag in self.taxonomy else "❌"
                    report += f"- `{note_path.name}` (tag: `{tag}`) {in_taxonomy}\n"
            except:
                pass

        report += f"\n## Tags Not in Taxonomy\n\n"

        missing_tags = []
        for note_path in old_notes:
            try:
                with open(note_path, 'r', encoding='utf-8') as f:
                    content = f.read(500)

                tag_match = re.search(r'^tag:\s*(.+)$', content, re.MULTILINE)
                if tag_match:
                    tag = tag_match.group(1).strip()
                    if tag not in self.taxonomy:
                        missing_tags.append(tag)
            except:
                pass

        if missing_tags:
            for tag in sorted(missing_tags):
                report += f"- `{tag}` - **Needs taxonomy entry**\n"
        else:
            report += "All tags have taxonomy entries ✅\n"

        return report


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Migrate tag notes to hierarchical schema")
    parser.add_argument("--vault", type=str, default="C:/obsidian-memory-vault",
                       help="Path to vault")
    parser.add_argument("--dry-run", action="store_true",
                       help="Preview changes without modifying files")
    parser.add_argument("--report", action="store_true",
                       help="Generate migration report")

    args = parser.parse_args()

    migrator = TagNoteMigrator(Path(args.vault))

    if args.report:
        report = migrator.generate_migration_report()
        report_path = Path(args.vault) / "_system" / "migration-report.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\n[OK] Migration Report Generated")
        print(f"   Report: {report_path}\n")

    else:
        stats = migrator.migrate_all(dry_run=args.dry_run)

        mode = "[DRY RUN]" if args.dry_run else "[OK]"
        print(f"\n{mode} Tag Note Migration")
        print(f"\n   Total: {stats['total']}")
        print(f"   Migrated: {stats['migrated']}")
        print(f"   Skipped: {stats['skipped']}")
        print(f"   Failed: {stats['failed']}")

        if args.dry_run:
            print(f"\n   Run without --dry-run to apply changes\n")
        else:
            print(f"\n   Migration complete!\n")


if __name__ == "__main__":
    main()
