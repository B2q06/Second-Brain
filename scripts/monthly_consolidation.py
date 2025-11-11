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

    def extract_monthly_updates(self, content: str) -> List[Dict]:
        """Extract all updates from current month."""
        updates = []

        # Find Recent Updates section
        section_match = re.search(
            r'## Recent Updates\s*\n(.*?)(?=\n##|\Z)',
            content,
            re.DOTALL
        )

        if not section_match:
            return updates

        updates_section = section_match.group(1)

        # Extract individual update entries
        update_pattern = rf'### (\d{{4}}-{self.current_month:02d}-\d{{2}}) \(Conversation: \[\[([^\]]+)\]\]\)\s*\n((?:- [^\n]+\n)*)'

        for match in re.finditer(update_pattern, updates_section):
            date_str = match.group(1)
            conversation = match.group(2)
            observations = [
                line.strip()[2:]  # Remove "- " prefix
                for line in match.group(3).split('\n')
                if line.strip().startswith('- ')
            ]

            updates.append({
                'date': date_str,
                'conversation': conversation,
                'observations': observations
            })

        return updates

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

    def compress_daily_entries(self, content: str) -> str:
        """Compress daily entries while preserving monthly summaries."""

        # Find Recent Updates section
        section_match = re.search(
            r'(## Recent Updates\s*\n)(.*?)((?=\n##|\Z))',
            content,
            re.DOTALL
        )

        if not section_match:
            return content

        section_header = section_match.group(1)
        updates_section = section_match.group(2)
        rest_of_content = section_match.group(3)

        # Compress updates from previous months (keep only date and conversation)
        def compress_update(match):
            date_str = match.group(1)
            conversation = match.group(2)
            observations = match.group(3)

            # Check if from current month
            try:
                update_date = datetime.strptime(date_str, "%Y-%m-%d")
                if update_date.month == self.current_month and update_date.year == self.current_year:
                    # Keep full entry for current month
                    return match.group(0)
                else:
                    # Compress older entries
                    return f"### {date_str} (Conversation: [[{conversation}]])\n*[Compressed - see monthly summary]*\n\n"
            except:
                return match.group(0)

        update_pattern = r'### (\d{4}-\d{2}-\d{2}) \(Conversation: \[\[([^\]]+)\]\]\)\s*\n((?:- [^\n]+\n)*)'
        compressed_updates = re.sub(update_pattern, compress_update, updates_section)

        # Reconstruct content
        before_section = content[:section_match.start()]
        after_section = content[section_match.end():]

        return before_section + section_header + compressed_updates + rest_of_content + after_section

    def process_tag_note(self, tag_note_path: Path) -> bool:
        """Process a single tag note for monthly consolidation."""
        try:
            print(f"\n[~] Processing: {tag_note_path.name}")

            # Read content
            with open(tag_note_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract tag name from frontmatter
            tag_match = re.search(r'^tag:\s*(.+)$', content, re.MULTILINE)
            if not tag_match:
                print(f"[!] Could not extract tag name")
                return False
            tag_name = tag_match.group(1).strip()

            # Check if monthly summary already exists for this month
            if f"## Monthly Summary ({self.month_name} {self.current_year})" in content:
                print(f"[i] Monthly summary already exists, skipping")
                return True

            # Extract updates from current month
            monthly_updates = self.extract_monthly_updates(content)

            if not monthly_updates:
                print(f"[i] No updates from {self.month_name}, skipping")
                return True

            print(f"[+] Found {len(monthly_updates)} update(s) from {self.month_name}")

            # Find related tags
            related_tags = self.find_related_tags(tag_name, content)
            print(f"[+] Identified {len(related_tags)} related tag(s)")

            # Generate monthly summary
            summary = self.generate_monthly_summary(tag_name, monthly_updates, related_tags)

            # Insert monthly summary before "## Related Tags" or at end
            summary_section = f"\n## Monthly Summary ({self.month_name} {self.current_year})\n\n{summary}\n"

            if "## Related Tags" in content:
                content = content.replace("## Related Tags", summary_section + "\n## Related Tags")
            elif "## Statistics" in content:
                content = content.replace("## Statistics", summary_section + "\n## Statistics")
            else:
                # Append at end
                content += summary_section

            # Compress older daily entries
            content = self.compress_daily_entries(content)

            # Update last_updated in frontmatter
            content = re.sub(
                r'^last_updated:\s*.+$',
                f'last_updated: {datetime.now().strftime("%Y-%m-%d")}',
                content,
                flags=re.MULTILINE
            )

            # Write back
            with open(tag_note_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"[✓] Monthly summary added")
            return True

        except Exception as e:
            print(f"[X] Error processing {tag_note_path}: {e}")
            import traceback
            traceback.print_exc()
            return False

    def run(self, force: bool = False):
        """Run monthly consolidation for all tag notes."""

        # Check if it's last day of month
        if not force and not self.is_last_day_of_month():
            print(f"[i] Not last day of month, use --force to run anyway")
            return

        print(f"\n{'='*60}")
        print(f"Monthly Consolidation: {self.month_name} {self.current_year}")
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
            if self.process_tag_note(tag_note):
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
    parser.add_argument("--force", action="store_true",
                       help="Force consolidation even if not last day of month")

    args = parser.parse_args()

    vault_path = Path(args.vault)
    if not vault_path.exists():
        print(f"[X] Vault not found: {vault_path}")
        sys.exit(1)

    consolidator = MonthlyConsolidation(vault_path)
    consolidator.run(force=args.force)


if __name__ == "__main__":
    main()
