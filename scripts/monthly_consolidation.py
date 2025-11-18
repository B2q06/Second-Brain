#!/usr/bin/env python3
"""
Monthly Consolidation Script
Generates holistic monthly summaries for all tag notes with cross-tag references.

Runs on last day of month or when manually triggered.
"""

import os
import sys
import re
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Set, Tuple

class MonthlyConsolidation:
    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.current_month = datetime.now().month
        self.current_year = datetime.now().year
        self.month_name = datetime.now().strftime("%B")

    def is_last_day_of_month(self) -> bool:
        """Check if today is the last day of the month."""
        today = datetime.now()
        tomorrow = today + timedelta(days=1)
        return tomorrow.month != today.month

    def find_all_tag_notes(self) -> List[Path]:
        """Find all tag notes in the vault."""
        tag_notes = []
        for md_file in self.vault_path.rglob("*.md"):
            # Skip if in certain directories
            if any(part in md_file.parts for part in ["00-Inbox", "_system", ".obsidian"]):
                continue

            # Read frontmatter to check if it's a tag note
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                if 'type: tag-note' in content[:500]:  # Check first 500 chars
                    tag_notes.append(md_file)
            except Exception as e:
                print(f"[!] Error reading {md_file}: {e}")

        return tag_notes

    def extract_monthly_entries(self, content: str, month: int, year: int) -> List[Dict]:
        """
        Extract all entries from a specific month section.

        Args:
            content: Tag note content
            month: Month number (1-12)
            year: Year (e.g., 2025)

        Returns:
            List of entry dicts with date, discussion, related_tags, source
        """
        import calendar
        month_name = calendar.month_name[month]

        # Find month section (e.g., "## November 2025")
        section_pattern = rf'## {month_name} {year}\s*\n(.*?)(?=\n##|\Z)'
        section_match = re.search(section_pattern, content, re.DOTALL)

        if not section_match:
            return []

        month_section = section_match.group(1)
        entries = []

        # Extract individual entries (### YYYY-MM-DD HH:MM format)
        entry_pattern = r'### (\d{4}-\d{2}-\d{2}(?: \d{2}:\d{2})?)\s*\n(.*?)(?=\n###|\Z)'

        for match in re.finditer(entry_pattern, month_section, re.DOTALL):
            date_str = match.group(1)
            entry_body = match.group(2).strip()

            # Parse entry body
            # Extract discussion (everything before Related/Source lines)
            discussion_lines = []
            related_tags = []
            source = None

            for line in entry_body.split('\n'):
                if line.startswith('**Related'):
                    # Extract wikilinks from Related line
                    related_tags = re.findall(r'\[\[([^\]]+)\]\]', line)
                elif line.startswith('**Source'):
                    # Extract source conversation link
                    source_match = re.search(r'\[\[([^\]]+)\]\]', line)
                    if source_match:
                        source = source_match.group(1)
                else:
                    # Part of discussion
                    if line.strip():
                        discussion_lines.append(line.strip())

            discussion = ' '.join(discussion_lines)

            entries.append({
                'date': date_str,
                'discussion': discussion,
                'related_tags': related_tags,
                'source': source
            })

        return entries

    def find_related_tags(self, tag_name: str, content: str) -> List[str]:
        """Find related tags from Related Tags section and cross-references in updates."""
        related = set()

        # From Related Tags section
        section_match = re.search(
            r'## Related Tags\s*\n(.*?)(?=\n##|\Z)',
            content,
            re.DOTALL
        )

        if section_match:
            # Extract all [[wikilinks]]
            for match in re.finditer(r'\[\[([^\]]+)\]\]', section_match.group(1)):
                related.add(match.group(1))

        # From update observations (co-mentioned tags)
        for match in re.finditer(r'\[\[([^\]]+)\]\]', content):
            related.add(match.group(1))

        # Remove self-reference
        related.discard(tag_name)

        return list(related)

    def generate_monthly_summary(
        self,
        tag_name: str,
        monthly_updates: List[Dict],
        related_tags: List[str]
    ) -> str:
        """Generate holistic monthly summary with cross-tag references."""

        if not monthly_updates:
            return f"*No updates recorded for {self.month_name} {self.current_year}*"

        # Aggregate all observations
        all_observations = []
        for update in monthly_updates:
            all_observations.extend(update['observations'])

        # Build summary prompt for LLM (would be called by agent)
        summary_context = {
            'tag': tag_name,
            'month': self.month_name,
            'year': self.current_year,
            'num_conversations': len(monthly_updates),
            'observations': all_observations,
            'related_tags': related_tags
        }

        # For now, generate a simple structured summary
        # In production, this would call an LLM to generate prose
        summary_lines = [
            f"This month's work with **{tag_name}** spanned {len(monthly_updates)} conversation(s)."
        ]

        # Group observations by theme (simple keyword matching)
        if all_observations:
            summary_lines.append("\n**Key developments:**")
            for obs in all_observations[:5]:  # Top 5 observations
                summary_lines.append(f"- {obs}")

        # Add cross-references
        if related_tags:
            summary_lines.append(f"\n**Related explorations:**")
            for related_tag in related_tags[:5]:  # Top 5 related
                summary_lines.append(f"- [[{related_tag}]]")

        return "\n".join(summary_lines)

    def compress_month_section(
        self,
        content: str,
        month: int,
        year: int,
        entries: List[Dict],
        all_related_tags: Set[str]
    ) -> str:
        """
        Compress a month section into a summary paragraph, preserving last-day entry.

        Args:
            content: Full tag note content
            month: Month to compress (1-12)
            year: Year to compress
            entries: All entries from this month
            all_related_tags: All unique related tags from the month

        Returns:
            Updated content with compressed month section
        """
        import calendar
        month_name = calendar.month_name[month]

        # Get last day of this month (leap year aware)
        last_day = calendar.monthrange(year, month)[1]
        last_day_str = f"{year}-{month:02d}-{last_day:02d}"

        # Separate last-day entry from others
        last_day_entry = None
        regular_entries = []

        for entry in entries:
            if entry['date'].startswith(last_day_str):
                last_day_entry = entry
            else:
                regular_entries.append(entry)

        # Generate compressed summary
        summary_parts = []

        if regular_entries or last_day_entry:
            summary_parts.append(
                f"This month's work spanned {len(entries)} conversation(s). "
            )

        # Consolidate key points from all discussions
        if regular_entries:
            # Take key sentences from discussions
            key_points = []
            for entry in regular_entries[:3]:  # Focus on first 3 entries
                if entry['discussion']:
                    # Take first sentence as key point
                    first_sentence = entry['discussion'].split('.')[0] + '.'
                    key_points.append(first_sentence)

            if key_points:
                summary_parts.append(' '.join(key_points))

        # Add cross-tag references
        if all_related_tags:
            summary_parts.append("\n\n**Related explorations:**")
            for tag in sorted(all_related_tags)[:8]:  # Top 8 related tags
                summary_parts.append(f"\n- [[{tag}]]")

        compressed_summary = '\n'.join(summary_parts)

        # Build new month section
        new_section_parts = [f"## {month_name} {year}\n"]
        new_section_parts.append(f"*Compressed from {len(regular_entries)} entries*\n\n")
        new_section_parts.append(compressed_summary)

        # Preserve last-day entry if it exists
        if last_day_entry:
            new_section_parts.append(f"\n\n### {last_day_entry['date']}")
            new_section_parts.append(f"\n{last_day_entry['discussion']}")

            if last_day_entry['related_tags']:
                related = ', '.join([f"[[{t}]]" for t in last_day_entry['related_tags']])
                new_section_parts.append(f"\n**Related**: {related}")

            if last_day_entry['source']:
                new_section_parts.append(f"\n**Source**: [[{last_day_entry['source']}]]")

        new_section = ''.join(new_section_parts)

        # Replace old month section with compressed version
        old_section_pattern = rf'## {month_name} {year}\s*\n.*?(?=\n##|\Z)'
        content = re.sub(old_section_pattern, new_section, content, flags=re.DOTALL)

        return content

    def compress_previous_month_if_needed(self, tag_note_path: Path, target_month: int = None, target_year: int = None) -> bool:
        """
        Check if we need to compress previous month and do it.

        Args:
            tag_note_path: Path to tag note
            target_month: Month to compress (if None, compress previous month)
            target_year: Year to compress (if None, use current year)

        Returns:
            True if compression performed or not needed, False on error
        """
        try:
            # Read content
            with open(tag_note_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Determine month to compress
            if target_month is None or target_year is None:
                # Calculate previous month
                if self.current_month == 1:
                    compress_month = 12
                    compress_year = self.current_year - 1
                else:
                    compress_month = self.current_month - 1
                    compress_year = self.current_year
            else:
                compress_month = target_month
                compress_year = target_year

            import calendar
            compress_month_name = calendar.month_name[compress_month]

            # Check if month section exists and isn't already compressed
            if f"## {compress_month_name} {compress_year}" not in content:
                return True  # Month doesn't exist, nothing to compress

            if f"*Compressed from" in content and f"## {compress_month_name} {compress_year}" in content:
                print(f"[i] {compress_month_name} {compress_year} already compressed")
                return True

            # Extract entries from the month
            entries = self.extract_monthly_entries(content, compress_month, compress_year)

            if not entries:
                print(f"[i] No entries found in {compress_month_name} {compress_year}")
                return True

            # Collect all related tags
            all_related = set()
            for entry in entries:
                all_related.update(entry['related_tags'])

            # Compress the month section
            content = self.compress_month_section(
                content,
                compress_month,
                compress_year,
                entries,
                all_related
            )

            # Write back
            with open(tag_note_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"[✓] Compressed {compress_month_name} {compress_year} ({len(entries)} entries)")
            return True

        except Exception as e:
            print(f"[X] Error compressing month: {e}")
            import traceback
            traceback.print_exc()
            return False

    def process_tag_note(self, tag_note_path: Path, compress_mode: bool = False) -> bool:
        """
        Process a single tag note for monthly consolidation.

        Args:
            tag_note_path: Path to tag note
            compress_mode: If True, compress previous month; if False, skip

        Returns:
            True on success, False on error
        """
        try:
            print(f"\n[~] Processing: {tag_note_path.name}")

            if compress_mode:
                # Just compress previous month
                return self.compress_previous_month_if_needed(tag_note_path)
            else:
                # Normal processing (when manually triggered)
                print(f"[i] Skipping (use --compress to compress previous month)")
                return True

        except Exception as e:
            print(f"[X] Error processing {tag_note_path}: {e}")
            import traceback
            traceback.print_exc()
            return False

    def run(self, compress: bool = False):
        """
        Run monthly consolidation for all tag notes.

        Args:
            compress: If True, compress previous month
        """
        print(f"\n{'='*60}")
        print(f"Monthly Consolidation: {self.month_name} {self.current_year}")
        if compress:
            print(f"Mode: Compress previous month")
        print(f"{'='*60}\n")

        # Find all tag notes
        tag_notes = self.find_all_tag_notes()
        print(f"[i] Found {len(tag_notes)} tag note(s)\n")

        if not tag_notes:
            print("[!] No tag notes found")
            return

        # Process each tag note
        success_count = 0
        for tag_note in tag_notes:
            if self.process_tag_note(tag_note, compress_mode=compress):
                success_count += 1

        print(f"\n{'='*60}")
        print(f"[✓] Consolidation complete")
        print(f"    Processed: {success_count}/{len(tag_notes)} tag notes")
        print(f"{'='*60}\n")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate monthly summaries for tag notes")
    parser.add_argument("--vault", type=str, help="Path to Obsidian vault",
                       default="C:/obsidian-memory-vault")
    parser.add_argument("--compress", action="store_true",
                       help="Compress previous month's entries")

    args = parser.parse_args()

    vault_path = Path(args.vault)
    if not vault_path.exists():
        print(f"[X] Vault not found: {vault_path}")
        sys.exit(1)

    consolidator = MonthlyConsolidation(vault_path)
    consolidator.run(compress=args.compress)


if __name__ == "__main__":
    main()
