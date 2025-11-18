#!/usr/bin/env python3
"""
Timeline Generator
Generates chronological timelines of conversations and knowledge growth
"""

import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from collections import defaultdict
from logger_setup import get_logger, TimedOperation


class TimelineGenerator:
    """Generate chronological timelines"""

    def __init__(self, vault_path: Path):
        self.vault_path = Path(vault_path)
        self.logger = get_logger(__name__, str(vault_path))

    def generate_full_timeline(self, output_file: Path = None) -> str:
        """Generate complete timeline of all conversations"""
        self.logger.info("Generating full timeline")

        if output_file is None:
            output_file = self.vault_path / "_system" / "timeline.md"

        # Collect all conversations
        conversations = self._collect_conversations()

        if not conversations:
            self.logger.warning("No conversations found")
            return ""

        # Sort by date
        conversations.sort(key=lambda x: x["date"])

        # Build timeline markdown
        timeline = "# Knowledge Timeline\n\n"
        timeline += f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        timeline += f"**Total conversations**: {len(conversations)}\n\n"
        timeline += "---\n\n"

        # Group by month
        by_month = defaultdict(list)
        for conv in conversations:
            month = conv["date"].strftime("%Y-%m")
            by_month[month].append(conv)

        # Build month sections
        for month in sorted(by_month.keys(), reverse=True):
            month_convs = by_month[month]
            month_date = datetime.strptime(month, "%Y-%m")
            month_name = month_date.strftime("%B %Y")

            timeline += f"## {month_name}\n\n"
            timeline += f"**{len(month_convs)} conversation(s)**\n\n"

            for conv in month_convs:
                date_str = conv["date"].strftime("%Y-%m-%d")
                timeline += f"### [{date_str}] {conv['title']}\n\n"
                timeline += f"**File**: `{conv['file_name']}`\n\n"

                if conv["entities"]:
                    timeline += f"**Entities**: "
                    timeline += ", ".join([f"[[{e}]]" for e in conv["entities"]])
                    timeline += "\n\n"

                if conv["tags"]:
                    timeline += f"**Tags**: "
                    timeline += ", ".join([f"#{t}" for t in conv["tags"]])
                    timeline += "\n\n"

                timeline += "---\n\n"

        # Save
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(timeline)

        self.logger.info(f"Timeline generated: {output_file}")
        return timeline

    def generate_weekly_timeline(self, weeks: int = 4, output_file: Path = None) -> str:
        """Generate timeline for last N weeks"""
        self.logger.info(f"Generating timeline for last {weeks} weeks")

        if output_file is None:
            output_file = self.vault_path / "_system" / f"timeline_last_{weeks}_weeks.md"

        # Collect conversations
        conversations = self._collect_conversations()

        if not conversations:
            return ""

        # Filter to last N weeks
        cutoff_date = datetime.now() - timedelta(weeks=weeks)
        recent = [c for c in conversations if c["date"] >= cutoff_date]

        if not recent:
            self.logger.warning(f"No conversations in last {weeks} weeks")
            return ""

        # Sort by date
        recent.sort(key=lambda x: x["date"])

        # Build timeline
        timeline = f"# Timeline: Last {weeks} Weeks\n\n"
        timeline += f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        timeline += f"**Conversations**: {len(recent)}\n\n"
        timeline += "---\n\n"

        # Group by week
        by_week = defaultdict(list)
        for conv in recent:
            week = conv["date"].strftime("%Y-W%W")
            by_week[week].append(conv)

        # Build week sections
        for week in sorted(by_week.keys(), reverse=True):
            week_convs = by_week[week]

            timeline += f"## Week {week}\n\n"
            timeline += f"**{len(week_convs)} conversation(s)**\n\n"

            for conv in week_convs:
                date_str = conv["date"].strftime("%Y-%m-%d")
                timeline += f"- **{date_str}**: [{conv['title']}]({conv['file_path']})\n"

                if conv["entities"]:
                    timeline += f"  - Entities: {', '.join([f'[[{e}]]' for e in conv['entities']])}\n"

            timeline += "\n"

        # Save
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(timeline)

        self.logger.info(f"Weekly timeline generated: {output_file}")
        return timeline

    def generate_entity_timeline(self, entity: str, output_file: Path = None) -> str:
        """Generate timeline for a specific entity"""
        self.logger.info(f"Generating timeline for entity: {entity}")

        if output_file is None:
            entity_slug = entity.replace(" ", "_").replace("/", "_")
            output_file = self.vault_path / "_system" / f"timeline_{entity_slug}.md"

        # Collect conversations mentioning entity
        conversations = self._collect_conversations()
        entity_convs = [c for c in conversations if entity in c["entities"]]

        if not entity_convs:
            self.logger.warning(f"No conversations found for entity: {entity}")
            return ""

        # Sort by date
        entity_convs.sort(key=lambda x: x["date"])

        # Build timeline
        timeline = f"# Timeline: {entity}\n\n"
        timeline += f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        timeline += f"**Total mentions**: {len(entity_convs)} conversation(s)\n\n"
        timeline += "---\n\n"

        # Chronological listing
        for i, conv in enumerate(entity_convs, 1):
            date_str = conv["date"].strftime("%Y-%m-%d")
            timeline += f"## {i}. [{date_str}] {conv['title']}\n\n"
            timeline += f"**File**: [{conv['file_name']}]({conv['file_path']})\n\n"

            # Other entities in same conversation
            other_entities = [e for e in conv["entities"] if e != entity]
            if other_entities:
                timeline += f"**Related entities**: "
                timeline += ", ".join([f"[[{e}]]" for e in other_entities])
                timeline += "\n\n"

            timeline += "---\n\n"

        # Save
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(timeline)

        self.logger.info(f"Entity timeline generated: {output_file}")
        return timeline

    def generate_area_timeline(self, area: str, output_file: Path = None) -> str:
        """Generate timeline for a specific knowledge area"""
        self.logger.info(f"Generating timeline for area: {area}")

        if output_file is None:
            output_file = self.vault_path / "_system" / f"timeline_area_{area}.md"

        # Find entities in area
        area_entities = self._get_entities_by_area(area)

        if not area_entities:
            self.logger.warning(f"No entities found for area: {area}")
            return ""

        # Collect conversations with these entities
        conversations = self._collect_conversations()
        area_convs = []

        for conv in conversations:
            if any(e in area_entities for e in conv["entities"]):
                area_convs.append(conv)

        if not area_convs:
            self.logger.warning(f"No conversations found for area: {area}")
            return ""

        # Sort by date
        area_convs.sort(key=lambda x: x["date"])

        # Build timeline
        timeline = f"# Timeline: {area} Knowledge Area\n\n"
        timeline += f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        timeline += f"**Conversations**: {len(area_convs)}\n"
        timeline += f"**Entities**: {len(area_entities)}\n\n"
        timeline += "---\n\n"

        # Group by month
        by_month = defaultdict(list)
        for conv in area_convs:
            month = conv["date"].strftime("%Y-%m")
            by_month[month].append(conv)

        for month in sorted(by_month.keys(), reverse=True):
            month_convs = by_month[month]
            month_date = datetime.strptime(month, "%Y-%m")
            month_name = month_date.strftime("%B %Y")

            timeline += f"## {month_name}\n\n"

            for conv in month_convs:
                date_str = conv["date"].strftime("%Y-%m-%d")
                timeline += f"- **{date_str}**: [{conv['title']}]({conv['file_path']})\n"

                # Show area entities
                conv_area_entities = [e for e in conv["entities"] if e in area_entities]
                if conv_area_entities:
                    timeline += f"  - Entities: {', '.join([f'[[{e}]]' for e in conv_area_entities])}\n"

            timeline += "\n"

        # Save
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(timeline)

        self.logger.info(f"Area timeline generated: {output_file}")
        return timeline

    def _collect_conversations(self) -> List[Dict]:
        """Collect all conversations with metadata"""
        conversations = []
        processed_dir = self.vault_path / "00-Inbox" / "processed"

        if not processed_dir.exists():
            return []

        for conv_file in processed_dir.glob("*.md"):
            try:
                with open(conv_file, 'r', encoding='utf-8') as f:
                    content = f.read(1500)

                # Extract frontmatter
                fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
                if not fm_match:
                    continue

                frontmatter = fm_match.group(1)

                # Extract fields
                title_match = re.search(r'^title:\s*"?(.+?)"?$', frontmatter, re.MULTILINE)
                date_match = re.search(r'created:\s*(\d{4}-\d{2}-\d{2})', frontmatter)
                entities_match = re.search(r'entities:\s*\[(.*?)\]', frontmatter, re.DOTALL)
                tags_match = re.search(r'tags:\s*\[(.*?)\]', frontmatter)

                if not date_match:
                    continue

                # Parse entities
                entities = []
                if entities_match:
                    entity_str = entities_match.group(1)
                    entities = [e.strip().strip('"').strip("'") for e in entity_str.split(',') if e.strip()]

                # Parse tags
                tags = []
                if tags_match:
                    tag_str = tags_match.group(1)
                    tags = [t.strip().strip('"').strip("'") for t in tag_str.split(',') if t.strip()]

                conversations.append({
                    "title": title_match.group(1) if title_match else conv_file.stem,
                    "date": datetime.strptime(date_match.group(1), "%Y-%m-%d"),
                    "entities": entities,
                    "tags": tags,
                    "file_name": conv_file.name,
                    "file_path": str(conv_file.relative_to(self.vault_path))
                })

            except Exception as e:
                self.logger.warning(f"Failed to parse {conv_file.name}: {e}")

        return conversations

    def _get_entities_by_area(self, area: str) -> List[str]:
        """Get all entity names in a specific area"""
        entities = []

        for md_file in self.vault_path.rglob("*.md"):
            if any(part in md_file.parts for part in ["00-Inbox", "_system", ".obsidian"]):
                continue

            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read(500)

                    if 'type: tag-note' not in content:
                        continue

                    root_match = re.search(r'root:\s*(\w+)', content)
                    if not root_match or root_match.group(1) != area:
                        continue

                    tag_match = re.search(r'^tag:\s*(.+)$', content, re.MULTILINE)
                    if tag_match:
                        entities.append(tag_match.group(1).strip())

            except:
                pass

        return entities


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate knowledge timelines")
    parser.add_argument("--vault", type=str, default="C:/obsidian-memory-vault",
                       help="Path to vault")
    parser.add_argument("--full", action="store_true",
                       help="Generate full timeline")
    parser.add_argument("--weeks", type=int, default=4,
                       help="Generate timeline for last N weeks")
    parser.add_argument("--entity", type=str,
                       help="Generate timeline for specific entity")
    parser.add_argument("--area", type=str,
                       help="Generate timeline for specific area")

    args = parser.parse_args()

    generator = TimelineGenerator(Path(args.vault))

    if args.full:
        timeline = generator.generate_full_timeline()
        conv_count = len(generator._collect_conversations())
        print(f"\n[OK] Full Timeline Generated")
        print(f"   Conversations: {conv_count}")

    elif args.entity:
        timeline = generator.generate_entity_timeline(args.entity)
        print(f"\n[OK] Entity Timeline Generated: {args.entity}")

    elif args.area:
        timeline = generator.generate_area_timeline(args.area)
        print(f"\n[OK] Area Timeline Generated: {args.area}")

    else:
        # Default: weekly
        timeline = generator.generate_weekly_timeline(weeks=args.weeks)
        print(f"\n[OK] Weekly Timeline Generated")
        print(f"   Last {args.weeks} weeks")

    print()


if __name__ == "__main__":
    main()
