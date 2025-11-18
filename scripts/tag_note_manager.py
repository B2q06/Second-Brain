"""
Tag Note Manager - Core system for creating and updating living tag notes

This module implements the semantic memory layer of the second brain system.
Each tag becomes a living note that accumulates knowledge over time through
timestamped entries from conversations, with monthly compression and cross-referencing.

CRITICAL: Only captures what the USER discussed about tags, never adds external knowledge.
"""

import re
import yaml
from pathlib import Path
from datetime import datetime, date
from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict
import calendar

# Fix import to work from vault root
try:
    from scripts.tag_path_resolver import TagPathResolver
except ImportError:
    from tag_path_resolver import TagPathResolver


class TagNoteManager:
    """Manages creation and updating of tag notes in hierarchical folders"""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.taxonomy_path = self.vault_path / "_system" / "tag-taxonomy.md"
        self.template_path = self.vault_path / "_system" / "tag-note-template.md"

        # Use TagPathResolver for taxonomy operations
        self.resolver = TagPathResolver(self.vault_path, self.taxonomy_path)
        self.tag_taxonomy = self.resolver.taxonomy

    def get_or_create_tag_path(self, tag_name: str) -> Path:
        """
        Resolve hierarchical folder path for a tag and create folders if needed

        Args:
            tag_name: Tag name (e.g., "FastAPI", "Python", "Chinese Grammar")

        Returns:
            Full path to tag note file (e.g., vault/Technology/Programming/Python/FastAPI.md)
        """
        # Normalize tag name
        normalized = tag_name.lower().replace(' ', '-').replace('_', '-')

        # Use resolver to get taxonomy path
        taxonomy_path = self.resolver.resolve_path(normalized)

        if taxonomy_path:
            # Parse path to build folder structure
            # Example: "Technology > Programming > Languages > Python"
            parts = [p.strip() for p in taxonomy_path.split('>')]

            # Build folder (all parts except tag name which is last)
            folder = self.vault_path / parts[0]
            for part in parts[1:-1]:
                folder = folder / part

            # Get canonical name for filename
            canonical = self.tag_taxonomy.get(normalized, {}).get('canonical', tag_name)
        else:
            # Fallback: Try to infer category or use default
            folder_path = self._infer_category(tag_name)
            folder = self.vault_path / Path(folder_path)
            canonical = tag_name

        # Ensure folders exist
        folder.mkdir(parents=True, exist_ok=True)

        # Tag note filename (use canonical name)
        filename = canonical.replace('/', '-').replace('\\', '-') + '.md'

        return folder / filename

    def _infer_category(self, tag_name: str) -> str:
        """
        Fallback category inference for tags not in taxonomy

        Args:
            tag_name: Tag name to categorize

        Returns:
            Folder path (e.g., "Technology/Uncategorized")
        """
        # Simple heuristics
        tech_keywords = ['python', 'api', 'database', 'framework', 'library', 'code', 'programming']
        language_keywords = ['chinese', 'grammar', 'language', 'pinyin', 'hanzi']

        tag_lower = tag_name.lower()

        if any(kw in tag_lower for kw in tech_keywords):
            return "Technology/Uncategorized"
        elif any(kw in tag_lower for kw in language_keywords):
            return "Language/Uncategorized"
        else:
            return "30-Resources/knowledge"  # Default fallback

    def extract_related_tags(self, all_entities: List[str], current_tag: str) -> List[str]:
        """
        Extract related tags from conversation entities (co-mentioned tags)

        Args:
            all_entities: All entities/tags from conversation
            current_tag: The tag we're currently updating

        Returns:
            List of related tag names (excluding current_tag)
        """
        related = [tag for tag in all_entities if tag.lower() != current_tag.lower()]
        return sorted(set(related))  # Unique, sorted

    def create_or_update_tag_note(
        self,
        tag_name: str,
        discussion_text: str,
        timestamp: datetime,
        conversation_link: str,
        related_tags: List[str],
        conversation_duration_minutes: int = 0
    ) -> Tuple[Path, bool]:
        """
        Create or update a tag note with a new monthly entry

        Args:
            tag_name: Tag name (e.g., "FastAPI")
            discussion_text: What user discussed about this tag (2-4 sentences)
            timestamp: When conversation occurred
            conversation_link: Wikilink to conversation (e.g., "[[conversation_20251111_...]]")
            related_tags: Other tags mentioned in same conversation
            conversation_duration_minutes: Duration of conversation in minutes

        Returns:
            (Path to tag note file, True if created new / False if updated existing)
        """
        tag_path = self.get_or_create_tag_path(tag_name)

        created_new = False

        # Check if tag note exists
        if not tag_path.exists():
            # Create new tag note from template
            self._create_new_tag_note(tag_path, tag_name, timestamp)
            created_new = True

        # Add monthly entry
        self._add_monthly_entry(
            tag_path,
            discussion_text,
            timestamp,
            conversation_link,
            related_tags
        )

        # Update metadata
        self._update_metadata(tag_path, timestamp, conversation_duration_minutes)

        return tag_path, created_new

    def _create_new_tag_note(self, tag_path: Path, tag_name: str, timestamp: datetime):
        """
        Create a new tag note from template

        Args:
            tag_path: Full path where tag note will be created
            tag_name: Display name of tag
            timestamp: Creation timestamp
        """
        # Normalize tag name for lookup
        normalized = tag_name.lower().replace(' ', '-').replace('_', '-')

        # Use resolver to get taxonomy data
        taxonomy_path = self.resolver.resolve_path(normalized)
        parent_tags = self.resolver.resolve_parent_tags(normalized)
        root = self.resolver.resolve_root(normalized)
        depth = self.resolver.resolve_depth(normalized)

        # Fallback if not in taxonomy
        if not taxonomy_path:
            # Build from file path
            relative_path = tag_path.parent.relative_to(self.vault_path)
            folder_parts = list(relative_path.parts)

            if folder_parts and folder_parts[0] not in ['30-Resources']:
                full_path_parts = folder_parts + [tag_name]
                taxonomy_path = ' > '.join(full_path_parts)
                root = folder_parts[0]
            else:
                taxonomy_path = f"Resources > {tag_name}"
                root = "Resources"

        # Build frontmatter
        frontmatter = {
            'type': 'tag-note',
            'tags': [normalized],  # 🔥 CRITICAL: Merges hashtag with note file
            'tag': normalized,
            'canonical': tag_name,
            'root': root or "Resources",
            'path': taxonomy_path,
            'parent_tags': parent_tags,
            'depth': depth or 1,
            'created': timestamp.strftime('%Y-%m-%d'),
            'last_updated': timestamp.strftime('%Y-%m-%d'),
            'total_conversations': 0,
            'total_time_minutes': 0
        }

        # Generate hierarchy section if parent tags exist
        hierarchy_section = ""
        if parent_tags:
            # Get canonical names for parent tags
            parent_links = []
            for parent in parent_tags:
                parent_canonical = self.tag_taxonomy.get(parent, {}).get('canonical', parent.replace('-', ' ').title())
                parent_links.append(f'[[{parent_canonical}]]')

            parent_chain = ' > '.join(parent_links)
            hierarchy_section = f"""
## Hierarchy
**Parent Categories**: {parent_chain}

"""

        # Create initial content
        content = f"""---
{yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True).strip()}
---

# {tag_name}
{hierarchy_section}
## Current Understanding
*To be developed through conversations*

## {timestamp.strftime('%B %Y')}

"""

        tag_path.write_text(content, encoding='utf-8')

    def _add_monthly_entry(
        self,
        tag_path: Path,
        discussion_text: str,
        timestamp: datetime,
        conversation_link: str,
        related_tags: List[str]
    ):
        """
        Add a timestamped entry to the current month section

        Args:
            tag_path: Path to existing tag note
            discussion_text: What user discussed about tag
            timestamp: When conversation occurred
            conversation_link: Wikilink to conversation
            related_tags: Other tags from conversation
        """
        content = tag_path.read_text(encoding='utf-8')

        # Month section header
        month_header = f"## {timestamp.strftime('%B %Y')}"

        # Entry format
        entry_time = timestamp.strftime('%Y-%m-%d %H:%M')
        entry = f"\n### {entry_time}\n{discussion_text}\n"

        # Add related tags if any
        if related_tags:
            related_links = ', '.join([f'[[{tag}]]' for tag in related_tags])
            entry += f"**Related**: {related_links}\n"

        # Add source conversation link
        entry += f"**Source**: {conversation_link}\n"

        # Check if month section exists
        if month_header in content:
            # Append to existing month section
            # Insert after month header but before next ## header
            lines = content.split('\n')
            new_lines = []
            in_current_month = False
            inserted = False

            for i, line in enumerate(lines):
                new_lines.append(line)

                # Found current month header
                if line.strip() == month_header:
                    in_current_month = True

                # Found next section header while in current month
                elif in_current_month and line.startswith('## ') and line.strip() != month_header:
                    # Insert entry before this next section
                    new_lines.insert(-1, entry)
                    inserted = True
                    in_current_month = False

            # If we reached end without finding next section, append
            if in_current_month and not inserted:
                new_lines.append(entry)

            content = '\n'.join(new_lines)
        else:
            # Create new month section
            # Insert after frontmatter and title, before first existing month section
            parts = content.split('## ')
            if len(parts) > 1:
                # Has existing sections
                content = parts[0] + month_header + '\n' + entry + '\n\n## ' + '## '.join(parts[1:])
            else:
                # No sections yet, append
                content += f'\n{month_header}\n{entry}\n'

        tag_path.write_text(content, encoding='utf-8')

    def _update_metadata(self, tag_path: Path, timestamp: datetime, duration_minutes: int = 0):
        """
        Update tag note frontmatter metadata

        Args:
            tag_path: Path to tag note
            timestamp: Latest update timestamp
            duration_minutes: Duration of this conversation in minutes
        """
        content = tag_path.read_text(encoding='utf-8')

        # Extract frontmatter
        match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not match:
            return

        frontmatter_text = match.group(1)
        frontmatter = yaml.safe_load(frontmatter_text)

        # Update fields
        frontmatter['last_updated'] = timestamp.strftime('%Y-%m-%d')
        frontmatter['total_conversations'] = frontmatter.get('total_conversations', 0) + 1
        frontmatter['total_time_minutes'] = frontmatter.get('total_time_minutes', 0) + duration_minutes

        # Replace frontmatter
        new_frontmatter = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True).strip()
        new_content = content.replace(
            f'---\n{frontmatter_text}\n---',
            f'---\n{new_frontmatter}\n---'
        )

        tag_path.write_text(new_content, encoding='utf-8')

    def should_compress_previous_month(self, current_date: datetime) -> Optional[Tuple[int, int]]:
        """
        Check if we're in a new month and should compress the previous month

        Args:
            current_date: Current conversation timestamp

        Returns:
            (year, month) of previous month if compression needed, None otherwise
        """
        # Get first day of current month
        first_of_month = current_date.replace(day=1)

        # Calculate previous month
        if first_of_month.month == 1:
            prev_month = 12
            prev_year = first_of_month.year - 1
        else:
            prev_month = first_of_month.month - 1
            prev_year = first_of_month.year

        return (prev_year, prev_month)

    def is_last_day_of_month(self, timestamp: datetime) -> bool:
        """
        Check if timestamp is on the last day of its month (leap year aware)

        Args:
            timestamp: Date to check

        Returns:
            True if this is the last day of the month
        """
        # Get last day of this month
        last_day = calendar.monthrange(timestamp.year, timestamp.month)[1]
        return timestamp.day == last_day


def main():
    """CLI interface for tag note manager"""
    import argparse

    parser = argparse.ArgumentParser(description='Manage tag notes in second brain system')
    parser.add_argument('--vault', required=True, help='Path to Obsidian vault')
    parser.add_argument('--conversation', help='Path to conversation file to process')
    parser.add_argument('--mode', choices=['update', 'test'], default='update')

    args = parser.parse_args()

    manager = TagNoteManager(args.vault)

    if args.mode == 'test':
        print("[*] Testing tag note manager...")
        print(f"[*] Vault: {manager.vault_path}")
        print(f"[*] Taxonomy entries: {len(manager.tag_taxonomy)}")

        # Test path resolution
        test_tags = ['Python', 'FastAPI', 'Neo4j', 'Chinese Grammar']
        for tag in test_tags:
            path = manager.get_or_create_tag_path(tag)
            print(f"[*] {tag} -> {path}")

    elif args.conversation:
        print(f"[*] Processing conversation: {args.conversation}")
        # This would be called by processing pipeline
        # For now, just a placeholder
        print("[!] Conversation processing requires integration with pipeline")


if __name__ == '__main__':
    main()
